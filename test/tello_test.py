import time, cv2, os
from threading import Thread
from djitellopy import Tello

# path info
save_vid_path = "/Users/kiwi8/Desktop/FALL QUARTER 2025/Research (AICPS)"
os.makedirs(save_vid_path, exist_ok=True)
save_file = os.path.join(save_vid_path, "video.mp4")

# connect to Tello
tello = Tello()
tello.connect()
dist = 30 #20cm

# ready to record
keepRecording = True
tello.streamon()
frame_read = tello.get_frame_read()

def take_pic(frame_read=None):
    pic_path = os.path.join(save_vid_path, "picture.png")
    frame = frame_read.frame
    if frame is None:
        return
    else:
        # RGB -> BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(pic_path, frame_bgr)
        print("Picture saved to:", pic_path)

def videoRecorder():
    # recording to ./video.avi
    while frame_read.frame is None:
        time.sleep(0.01)
    frame = frame_read.frame
    h, w = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    video = cv2.VideoWriter(save_file, fourcc, fps, (w, h))

    print("Video recording started.")
    while keepRecording:
        frame = frame_read.frame
        if frame is not None:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            video.write(frame_bgr)
        time.sleep(1 / fps)
    video.release()
    print("Video recording stopped.")

def simple_flying_test(tello, frame_read, dist):
    tello.takeoff()
    time.sleep(2)
    tello.rotate_clockwise(180)
    time.sleep(1)
    take_pic(frame_read)
    tello.move_forward(dist)
    time.sleep(1)
    tello.move_up(dist)
    time.sleep(1)
    tello.rotate_counter_clockwise(180)
    time.sleep(1)
    tello.flip_forward()
    time.sleep(2)
    tello.land()

battery = tello.get_battery()
print(f"The battery is {battery}%")
option = input("y or n: ")
if battery >= 40 and option == 'y':
    recorder = Thread(target=videoRecorder)
    recorder.start()
    try:
        simple_flying_test(tello, frame_read, dist)
    except Exception as e:
        print("Error: ", e)
    finally:
        keepRecording = False
        recorder.join()
        frame_read.stop()
        tello.streamoff()
        tello.end()
    print("Recording saved to:", save_file)
else:
    tello.streamoff()
    tello.end()