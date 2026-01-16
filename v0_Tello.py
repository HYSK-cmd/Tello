from typing import Tuple
import time
from djitellopy import TelloException
from occupancy_map import OccupancyGrid, ValueMap, Pose2D
from tello_wrapper import TelloWrapper


# You can modify the configuration of the spatial map here
class MyConfig:
    WIDTH = 50
    HEIGHT = 50
    CELL_SIZE = 0.1

def test_spatial_memory(tello: TelloWrapper, wp: list, wp_record: list, occupancy_grid: OccupancyGrid, value_map: ValueMap):
    try:
        # Get delta movement
        delta_pose = move_drone(tello, wp)
        if delta_pose is None:
            print("Failed to execute waypoint")
            return False
        
        # Get previous position
        prev_pos = Pose2D(x=occupancy_grid.curr_point.x, y=occupancy_grid.curr_point.y, yaw=occupancy_grid.curr_point.yaw)
        
        # Update drone position first to get new absolute position
        occupancy_grid.update_drone_pos_and_ori(delta_pose)
        
        # Get new position after update
        new_pos = Pose2D(x=occupancy_grid.curr_point.x, y=occupancy_grid.curr_point.y, yaw=occupancy_grid.curr_point.yaw)
        
        # Now update the visited cells with absolute positions
        print("Updating the map...")
        occupancy_grid.update_visited_in_occup_grid(new_pos, prev_pos)
        print_occup_map(occupancy_grid, prev_pos, new_pos)
        
        wp_record.append(new_pos)
        time.sleep(1)  # Wait after each command
        return True
    except TelloException as e:
        print(f"Tello error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def move_drone(tello: TelloWrapper, wp: list):
    import math
    try:
        if wp[0] == "move_forward":
            tello.move_forward(wp[1])
            # Return delta movement in cm
            pose = Pose2D(x=0.0, y=float(wp[1]), yaw=0.0)
        elif wp[0] == "turn_cw":
            tello.turn_cw(wp[1])
            # Convert degrees to radians for yaw
            pose = Pose2D(x=0.0, y=0.0, yaw=math.radians(float(wp[1])))
        else:
            return None
        return pose
    except TelloException as e:
        print(f"Movement failed: {e}")
        raise

def print_occup_map(occupancy_grid: OccupancyGrid, pose1, pose2):
    print(f"Prev pose: ({pose1.x:.2f}, {pose1.y:.2f}, {pose1.yaw:.2f}rad)")
    print(f"New pose: ({pose2.x:.2f}, {pose2.y:.2f}, {pose2.yaw:.2f}rad)")
    start = occupancy_grid.world_to_cells(pose1.x, pose1.y)
    end = occupancy_grid.world_to_cells(pose2.x, pose2.y)
    print(f"Start cell: {start}, End cell: {end}")

    # Print only the relevant section (around the path)
    symbols = {
        0: '·',  # UNKNOWN
        1: ' ',  # FREE
        2: 'X',  # VISITED
        3: '#'   # OBSTACLE
    }
    x_min, x_max = min(start[0], end[0]) - 5, max(start[0], end[0]) + 5
    y_min, y_max = min(start[1], end[1]) - 5, max(start[1], end[1]) + 5
    print(f"\nShowing region: rows {y_min}-{y_max}, cols {x_min}-{x_max}\n")
    for row in occupancy_grid.grid[480:520+1]:
        print(''.join(symbols.get(cell, '?') for cell in row[480:520+1]))

def init_spatial_map() -> Tuple[OccupancyGrid, ValueMap]:
    occupancy_grid = OccupancyGrid(MyConfig.WIDTH, MyConfig.HEIGHT, MyConfig.CELL_SIZE)
    value_map = ValueMap.from_occupancy(occupancy_grid)
    return occupancy_grid, value_map

def main():
    tello = TelloWrapper()
    occupancy_grid, value_map = init_spatial_map()
    tello.connect()
    tello.start_stream()
    waypoints = [["move_forward", 25], ["turn_cw", 90], ["move_forward", 50], ["turn_cw", 90], ["move_forward", 35], ["turn_cw", 90], "move_forward", 15]
    wp_record = [] 
    try:
        if input("run it? [y/n]") == 'y':
            tello.takeoff()
            time.sleep(1)  # Stabilize after takeoff
            while tello.is_battery_good():
                for wp in waypoints:
                    if not tello.is_battery_good():
                        print("Battery too low, landing...")
                        break
                    if input("Next Waypoint?: [y/n]") == 'y':
                        success = test_spatial_memory(tello, wp, wp_record, occupancy_grid, value_map)
                        if not success:
                            print("Waypoint failed, stopping...")
                            break
                    else:
                        break
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error during flight: {e}")
    finally:
        tello.stop_stream()
        tello.land()

if __name__ == "__main__":
    main()