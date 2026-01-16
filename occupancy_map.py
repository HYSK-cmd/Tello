import numpy as np
import math
import logging
from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple, Optional

class Cell(IntEnum):
    UNKNOWN = 0
    FREE = 1
    VISITED = 2
    OBSTACLE = 3

@dataclass
class Pose2D:
    x: float
    y: float
    yaw: float # radians

def wrap_angle_rad(a: float) -> float:
    #normalize angle to (-π ~ π) 
    while a <= -math.pi:
        a += 2*math.pi
    while a >= math.pi:
        a -= 2*math.pi
    return a

class OccupancyGrid:
    # create a static-sized 2d map
    def __init__(self, W:int, H:int, cell_size: float, 
                 initial_xy: Tuple[float, float] = (0.0, 0.0)):
        self.W = W
        self.H = H
        self.cell_size = cell_size
        self.map_size_N = int((max(W, H) * 2) / cell_size)
        self.initial_x, self.initial_y = initial_xy
        self.center_offset = self.map_size_N // 2
        self.initial_sector = "N"
        self.curr_point = Pose2D(x=float(self.center_offset), y=float(self.center_offset), yaw=0.0)
        self.grid = np.full((self.map_size_N, self.map_size_N), Cell.UNKNOWN, dtype=np.int8)
    # coordinate transforms
    # args x, y are in CELL coordinates (not world cm)
    def world_to_cells(self, x: float, y:float) -> Optional[Tuple[int, int]]:
        # x, y are already cell coordinates from curr_point
        cx = int(round(x))
        cy = int(round(y))
        if 0 <= cx < self.map_size_N and 0 <= cy < self.map_size_N:
            return (cx, cy)
        return None
    def cells_to_world(self, cx: int, cy: int) -> Tuple[float, float]:
        x = (self.initial_x + ((cx - self.center_offset) + 0.5) * self.cell_size) * 100
        y = (self.initial_y + ((cy - self.center_offset) + 0.5) * self.cell_size) * 100
        x_m, y_m= round(x, 3), round(y, 3) # round up to 3 decimals
        return (x_m, y_m)
    # convert radian to degree
    def rad_to_deg(self, yaw: float):
        return math.degrees(wrap_angle_rad(yaw))
    # yaw 22.5 deg sector N, NE1, NE2, E, etc ...
    def determine_sec(self, yaw: float) -> str:
        sec_dict = {
            0:"N", 
            1:"NNE", 2:"NE", 3:"ENE", 
            4:"E",
            5:"ESE", 6:"ES", 7:"SSE", 
            8:"S",
            9:"SSW", 10:"SW", 11:"WSW",
            12:"W",
            13:"WNW", 14:"NW", 15:"NNW"
        }
        yaw_deg = self.rad_to_deg(yaw) % 360
        idx = math.floor((yaw_deg + 11.25) / 22.5) % 16
        return sec_dict[idx]
    # update visited area in 2D occupancy map
    def update_visited_in_occup_grid(self, point: Pose2D, prev_pos: Pose2D) -> None:
        start_point = self.world_to_cells(prev_pos.x, prev_pos.y)
        end_point = self.world_to_cells(point.x, point.y)
        if start_point is None or end_point is None:
            return
        x0, y0 = start_point
        x1, y1 = end_point

        dx, dy = abs(x1 - x0), abs(y1 - y0)
        x_update = 1 if x0 < x1 else -1 # x0 < x1 x must increase otherwise decrease
        y_update = 1 if y0 < y1 else -1 # here applies the same
        err = dx - dy
        x, y = x0, y0 
        # loop from start to end point
        while True:
            if self.grid[y][x] != Cell.OBSTACLE: # will be changed to == Cell.FREE
                self.grid[y][x] = Cell.VISITED
            if x == x1 and y == y1:
                break
            e2 = 2*err 
            # move in x-axis
            if e2 > -dy:
                err -= dy
                x += x_update
            # move in y-axis
            if e2 < dx:
                err += dx 
                y += y_update
        
    # update drone's current position and orientation in occupancy map
    def update_drone_pos_and_ori(self, point: Optional[Pose2D] = None):
        # return format = [(x, y, yaw), sector]
        if point is None:
            sector = self.determine_sec(self.curr_point.yaw)
            return [self.curr_point, sector]
        
        # point contains DELTA movement (in cm for x,y, radians for yaw)
        # Convert cm to meters, then to cells
        dx_m = point.x * 0.01  # cm to meters
        dy_m = point.y * 0.01  # cm to meters
        
        # Rotate delta movement by current yaw to get world coordinates
        cos_yaw = math.cos(self.curr_point.yaw)
        sin_yaw = math.sin(self.curr_point.yaw)
        dx_world = dx_m * cos_yaw - dy_m * sin_yaw
        dy_world = dx_m * sin_yaw + dy_m * cos_yaw
        
        # Convert to cells
        dx_cell = dx_world / self.cell_size
        dy_cell = dy_world / self.cell_size
        
        # Update position in cell coordinates
        self.curr_point.x += dx_cell
        self.curr_point.y += dy_cell
        
        # Update yaw (already in radians)
        self.curr_point.yaw = wrap_angle_rad(self.curr_point.yaw + point.yaw)
        
        # Clamp x, y to map bounds
        self.curr_point.x = min(max(self.curr_point.x, 0.0), self.map_size_N - 1.0)
        self.curr_point.y = min(max(self.curr_point.y, 0.0), self.map_size_N - 1.0)
        
        # Identify sector
        sector = self.determine_sec(self.curr_point.yaw)
        update_pos = [(self.curr_point.x, self.curr_point.y, self.curr_point.yaw), sector]
        return update_pos
    # get drone's current position in map
    def get_curr_pos_in_map(self):
        return self.curr_point
    # update occup_map
    def update_occup_map(self):
        # mark cells as FREE, OBSTACLE
        pass

class ValueMap(OccupancyGrid):
    def __init__(self, W:int, H:int, cell_size: float, 
                 initial_xy: Tuple[float, float] = (0.0, 0.0)):
        super().__init__(W, H, cell_size, initial_xy)
        self.value = np.zeros((self.map_size_N, self.map_size_N), dtype=np.float32)
        self.conf = np.zeros((self.map_size_N, self.map_size_N), dtype=np.float32)
        self.n = np.zeros((self.map_size_N, self.map_size_N), dtype=np.int32)
    @classmethod
    def from_occupancy(cls, om: "OccupancyGrid") -> "ValueMap":
        vm = cls(om.W, om.H, om.cell_size)
        return vm
    # define confidence value based on FOV 
    # theta = 0 -> cos(0) -> 1 highest trust value
    # theta = 1 -> cos(1) -> 0 lowest trust value
    def angle_confidence(self, theta: float, fov_rad: float) -> float:
        half = fov_rad / 2.0
        if half <= 1e-9:
            return 0.0
        t = abs(theta) / half
        if t >= 1.0:
            return 0.0
        return (math.cos(t * (math.pi / 2.0)) ** 2)
    def update_value_map(self, value_score: float, pose: Pose2D, fov_deg: float = 82.0, 
                         max_range_m: int = 4, use_obstacle_mask:bool = True) -> None:
        fov_rad = math.radians(fov_deg)
        half_fov = fov_rad / 2.0
        cx0 = int(pose.x * 0.01 / self.cell_size + int(self.curr_point.x) + 1e-9)
        cy0 = int(pose.y * 0.01 / self.cell_size + int(self.curr_point.y) + 1e-9)
        if not (0 <= cx0 <= self.map_size_N and 0 <= cy0 <= self.map_size_N):
            logging.warning("waypoint is larger than the map size")
            return None
        
        r_cells = math.ceil(max_range_m)
        x_min = max(0, int(self.curr_point.x) - r_cells)
        x_max = min(self.map_size_N - 1, int(self.curr_point.x) + r_cells)
        y_min = max(0, int(self.curr_point.y) - r_cells)
        y_max = min(self.map_size_N - 1, int(self.curr_point.y) + r_cells)

        for cy in range(y_min, y_max+1):
            for cx in range(x_min, x_max+1):
                dx = (cx + 0.5) - (self.curr_point.x + 0.5)
                dy = (cy + 0.5) - (self.curr_point.y + 0.5)
                dist = math.hypot(dx, dy)
                if dist > r_cells:
                    continue
                # Convert from math convention (East=0) to navigation convention (North=0)
                # atan2(dy, dx) gives angle from East, so we subtract from pi/2 to get angle from North
                angle = math.atan2(dx, dy)  # North=0, East=90, South=180, West=270
                theta = abs(wrap_angle_rad(angle - self.curr_point.yaw))
                if theta > half_fov:
                    continue
                c_curr = self.angle_confidence(theta, fov_rad)

                if use_obstacle_mask and self.grid[cy, cx] == Cell.OBSTACLE:
                    continue

                c_prev = float(self.conf[cy, cx])
                v_prev = float(self.value[cy, cx])
                self.n[cy, cx] += 1

                if c_prev <= 1e-9:
                    self.value[cy, cx] = value_score * c_curr
                    self.conf[cy, cx] = c_curr
                else:
                    v_new = ((((self.n[cy, cx] - 1) / self.n[cy, cx]) * v_prev) + ((1 / self.n[cy, cx]) * value_score)) * c_curr
                    c_new = (c_curr*c_curr + c_prev*c_prev) / (c_curr + c_prev)
                    self.value[cy, cx] = v_new
                    self.conf[cy, cx] = c_new
        return None
    
    def find_optimal_point(self, pose: Pose2D, max_range_m: int = 4, fov_deg: float = 82.0):
        cx0 = int(pose.x * 0.01 / self.cell_size + int(self.curr_point.x) + 1e-9)
        cy0 = int(pose.y * 0.01 / self.cell_size + int(self.curr_point.y) + 1e-9)
        r_cells = math.ceil(max_range_m)
        x_min = max(0, int(self.curr_point.x) - r_cells)
        x_max = min(self.map_size_N - 1, int(self.curr_point.x) + r_cells)
        y_min = max(0, int(self.curr_point.y) - r_cells)
        y_max = min(self.map_size_N - 1, int(self.curr_point.y) + r_cells)

        max_value = -1
        point = (self.center_offset, self.center_offset)
        fov_rad = math.radians(fov_deg)
        half_fov = fov_rad / 2
        for cy in range(y_min, y_max+1):
            for cx in range(x_min, x_max+1):
                dx = (cx + 0.5) - (self.curr_point.x + 0.5)
                dy = (cy + 0.5) - (self.curr_point.y + 0.5)
                dist = math.hypot(dx, dy)
                if dist > r_cells:
                    continue
                angle = math.atan2(dx, dy)  # North=0, East=90, South=180, West=270
                theta = abs(wrap_angle_rad(angle - self.curr_point.yaw))
                if theta > half_fov:
                    continue
                if self.value[cy, cx] > max_value:
                    max_value = self.value[cy, cx]
                    point = (cy, cx)
        return point

def initialize_occup_map(width=50, height=50, cell_size=0.1):
    occup_map = OccupancyGrid(width, height, cell_size)
    return occup_map

vm = ValueMap(50, 50, 0.1)
pose2 = Pose2D(x=50.0, y=30.0, yaw=math.pi/2)
vm.update_value_map(0.73, pose2)