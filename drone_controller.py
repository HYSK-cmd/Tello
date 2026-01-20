import os, cv2, time, logging
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Tuple, Optional
from dotenv import load_dotenv
from datetime import datetime
from Scorer.detect_objects import vision_detect
from occupancy_map import OccupancyGrid, ValueMap
from tello_wrapper import TelloWrapper
from google import genai

load_dotenv()
api_key = os.environ.get("GENAI_API_KEY")

class Agent:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
        self.lock = threading.Lock()
        self.is_updating = False

class Scorer(Agent):
    def __init__(self, executor: ThreadPoolExecutor):
        super().__init__()
        self.executor = executor
        self.llm_future = None

    def detect_objects(self, image_path):
        return vision_detect(image_path)
    
    def _call_llm_api(self, image_path: str, instruction: str):
        logging.info(f"LLM analyzing: {image_path}, instruction: {instruction}")
        # return [{"object": "person with umbrella", "bbox": [...], "score": 0.95}]
        return []
    
    def measure_coordinate_and_store(self, detections):
        pass
    def score_yaw_direction_in_image(self, ) -> Tuple[float, float]:
        pass

class Selector(Agent):
    def __init__(self):
        super().__init__()
    def select_detections(self, ):
        pass
    def select_free_points(self,):
        pass

# You can modify the configuration of the spatial map here
class MyConfig:
    WIDTH = 50
    HEIGHT = 50
    CELL_SIZE = 0.1

def predict_movement(
        tello: TelloWrapper, 
        occupancy_grid: OccupancyGrid, 
        value_map: ValueMap,
        score_agent: Scorer, 
        select_agent: Selector,
    ):

    image_path = get_image_from_drone(tello)
    if image_path is None:
        logging.warning("Failed to get image from drone")
        return
    # Execute Scorer Agent
    detections = score_agent.detect_objects(image_path)
    #instruction = "Find a person holding an umbrella"
    score_agent.measure_coordinate_and_store(detections)
    occup_score, value_score = score_agent.score_yaw_direction_in_image()

    occupancy_grid.update_occup_map(occup_score)
    value_map.update_value_map(value_score)
    
    # Execute Selector Agent
    candidate_detections = select_agent.select_detections()
    candidate_free_points = select_agent.select_free_points()
    
    # 이제 LLM 결과 필요할 때 가져오기 (여기서 블로킹)
    #llm_detections = llm_future.result()
    
    point = value_map.find_optimal_point()

    #move_drone()
    occupancy_grid.update_visited_in_occup_grid()
    occupancy_grid.update_drone_pos_and_ori() 

def get_image_from_drone(tello: TelloWrapper):
    fr = tello.get_frame_reader()
    if fr is None:
        return None
    frame = fr.frame
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = os.path.join('/FOV', f"frame_{ts}.png")
    img_saved = cv2.imwrite(image_path, frame)
    if not img_saved:
        logging.warning("IMAGE NOT SAVED")
        return None
    return image_path

def enable_agents(executor: ThreadPoolExecutor) -> Tuple[Scorer, Selector]:
    score_agent = Scorer(executor)
    select_agent = Selector(executor)
    return score_agent, select_agent

def init_spatial_map() -> Tuple[OccupancyGrid, ValueMap]:
    occupancy_grid = OccupancyGrid(MyConfig.WIDTH, MyConfig.HEIGHT, MyConfig.CELL_SIZE)
    value_map = ValueMap.from_occupancy(occupancy_grid)
    return occupancy_grid, value_map

def main():
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="LLM-Worker")
    
    tello = TelloWrapper()
    occupancy_grid, value_map = init_spatial_map()
    score_agent, select_agent = enable_agents(executor)

    tello.connect()
    tello.start_stream()
    try:
        while tello.is_battery_good():
            predict_movement(tello, occupancy_grid, value_map, score_agent, select_agent)
    finally:
        logging.info("Shutting down executor...")
        executor.shutdown(wait=True)  # 모든 LLM 작업 완료 대기
        tello.stop_stream()
        tello.land()

if __name__ == "__main__":
    main()
