import os, cv2, time, logging, argparse
import concurrent.futures # create a background server for llm API
import threading

from typing import Tuple, Optional
from dotenv import load_dotenv
from datetime import datetime

from occupancy_map import OccupancyGrid, ValueMap
from tello_wrapper import TelloWrapper
#from google.cloud import vision
from google import genai

load_dotenv()

api_key = os.environ.get("GENAI_API_KEY")
client = genai.Client(api_key=api_key)

parser = argparse.ArgumentParser()
parser.add_argument('--img_save_path', type=str, required=True)
args = parser.parse_args()

os.makedirs(args.img_save_path, exist_ok=True)
class Agent:
    def __init__(self,):
        self.lock = threading.Lock()
        self.is_updating = False

class Scorer(Agent):
    def __init__(self):
        super().__init__()
    def measure_coordinate_and_store(self,):
        pass
    def score_yaw_direction_in_image(self, ) -> Tuple[float, float]:
        pass

class Selector(Agent):
    def __init__(self,):
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

    image = capture_frame(tello)
    instruction = "Find a person holding an umbrella"
    detections = score_agent.detect_objects_with_llm(image, instruction)
    score_agent.measure_coordinate_and_store()
    occup_score, value_score = score_agent.score_yaw_direction_in_image()
    occupancy_grid.update_occup_map(occup_score)
    value_map.update_value_map(value_score)

    candidate_detections = select_agent.select_detections()
    candidate_free_points = select_agent.select_free_points()

    point = value_map.find_optimal_point()
    #move_drone()
    occupancy_grid.update_visited_in_occup_grid()
    occupancy_grid.update_drone_pos_and_ori()

def test_spatial_memory(tello: TelloWrapper, occupancy_grid: OccupancyGrid, value_map: ValueMap):
    image = capture_frame(tello)
    

def capture_frame(tello: TelloWrapper):
    fr = tello.get_frame_reader()
    if fr is None:
        return None
    frame = fr.frame
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = os.path.join(args.img_save_path, f"frame_{ts}.png")
    img_saved = cv2.imwrite(image_path, frame)
    if not img_saved:
        logging.warning("IMAGE NOT SAVED")
        return None
    return frame

def enable_agents() -> Tuple[Scorer, Selector]:
    score_agent = Scorer()
    select_agent = Selector()
    return score_agent, select_agent

def init_spatial_map() -> Tuple[OccupancyGrid, ValueMap]:
    occupancy_grid = OccupancyGrid(MyConfig.WIDTH, MyConfig.HEIGHT, MyConfig.CELL_SIZE)
    value_map = ValueMap.from_occupancy(occupancy_grid)
    return occupancy_grid, value_map

def main():
    tello = TelloWrapper()
    #score_agent, select_agent = enable_agents()
    occupancy_grid, value_map = init_spatial_map()
    tello.connect()
    tello.start_stream()
    try:
        while tello.is_battery_good():
            #predict_movement(tello, occupancy_grid, value_map, score_agent, select_agent)
            test_spatial_memory(tello, occupancy_grid, value_map)
    finally:
        tello.stop_stream()
        tello.land()

if __name__ == "__main__":
    main()