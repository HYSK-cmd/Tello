# ===========================================================================
# tools/libraries required
from google import genai 
from dotenv import load_dotenv
#from PIL import Image
from tello_wrapper import TelloWrapper
from prompts import nav_prompt_vanilla
import matplotlib.pyplot as plt
import os, time, cv2
import logging
# ===========================================================================
# get api_key
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=api_key)
# ===========================================================================
# global variables
gemini_model = "gemini-2.5-flash"
path = ""
save_path = os.path.join(path, "frame")
os.makedirs(save_path, exist_ok=True)
img_num = 0
# ===========================================================================
def observe_surrounding(tello: TelloWrapper) -> str:
    direction = {0: "front", 1: "right", 2: "rear", 3: "left"}
    image_list = []
    for i in range(4):
        tello.turn_cw(90)
        fr = tello.get_frame_reader()
        if fr is not None:
            frame = fr.frame
            image_name = f"{direction[i]}.png"
            save_image_path = os.path.join(save_path, image_name)
            if cv2.imwrite(save_image_path, frame):
                image_list.append(save_image_path)
    # open images and save for an upload
    uploaded_files = []
    for path in image_list:
        f = client.files.upload(file=path)
        uploaded_files.append(f)

    # ask gemini
    parts = [*uploaded_files, nav_prompt_vanilla] # need to replace nav_target_desc with an actual instruction
    response = client.models.generate_content(
        model=gemini_model,
        contents=parts,
    )
    return response.text
# ===========================================================================
def util_LLM(file: genai.types.File, prompt: str = None) -> str:
    parts = [file]
    if prompt is not None:
        parts.append(prompt)

    response = client.models.generate_content(
        model=gemini_model,
        contents=parts
    )
    return response.text
# ===========================================================================
def take_pic() -> str:
    global img_num
    fr = tello.get_frame_reader()
    if fr is None:
        return
    frame = fr.frame
    image_path = os.path.join(save_path, f"frame{img_num}.png")
    cv2.imwrite(image_path, frame)
    img_num += 1 # prevent from overwriting the same file
    return image_path
# ===========================================================================
def upload(path: str):
    return client.files.upload(file=path)
# ===========================================================================
def move_drone(tello: TelloWrapper, result:str, dist:int=0, degree:int=0):
    tello.keep_active()
    global flag
    match result:
        case "move_forward":
            tello.move_forward(dist)
        case "move_backward":
            tello.move_backward(dist)
        case "move_left":
            tello.move_left(dist)
        case "move_right":
            tello.move_right(dist)
        case "move_up":
            tello.move_up(dist)
        case "move_down":
            tello.move_down(dist)
        case "turn_cw":
            tello.turn_cw(degree)
        case "turn_ccw":
            tello.turn_ccw(degree)
        case "hover":
            pass
        case "stop":
            flag = 0
            tello.stop_stream()
            tello.land()
        case _:
            logging.error("unknown command")
            return
    return
# ===========================================================================
if __name__ == "__main__":
    flag = 0

    movement = ["move_forward", "move_backward", "move_left", "move_right", "move_up", "move_down"]
    turn = ["turn_cw", "turn_ccw"]
    pause = ["hover", "stop"]

    tello = TelloWrapper()
    tello.connect()
    tello.start_stream()
    
    if tello.is_battery_good():
        flag = 1
        tello.takeoff()
        time.sleep(2)
        out = observe_surrounding(tello).strip() # rotate to observe the surroundings (4 directions)
        parts = out.split()
        result = parts[0]
        dist = int(parts[1]) if len(parts) > 1 else 0
        if result in movement:
            move_drone(tello, result=result, dist=dist)
        elif result in turn:
            move_drone(tello, result=result, degree=dist)
        elif result in pause:
            move_drone(tello, result=result)

    while flag and tello.is_battery_good():
        if not flag:
            break
        path = take_pic()

        if path is None:
            logging.error("Failed to capture frame")
            continue

        my_file = upload(path)
        out = util_LLM(my_file).strip(); parts = out.split()
        result = parts[0]
        if not parts:
            logging.error("Empty LLM response")
            continue

        dist = int(parts[1]) if len(parts) > 1 else 0
        if result in movement:
            move_drone(tello, result=result, dist=dist)
        elif result in turn:
            move_drone(tello, result=result, degree=dist)
        elif result in pause:
            move_drone(tello, result=result)
        else:
            logging.error("unknown command")
    
    tello.stop_stream()
    tello.land()
    