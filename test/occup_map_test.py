import sys
import math
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from occupancy_map import initialize_occup_map, OccupancyGrid, Pose2D

map = initialize_occup_map()
pose1 = Pose2D(x=0.0, y=0.0, yaw=math.pi/2)
pose2 = Pose2D(x=30.0, y=10.0, yaw=math.pi/2)

# Debug: see what cells we're working with
start = map.world_to_cells(pose1.x, pose1.y)
end = map.world_to_cells(pose2.x, pose2.y)
print(f"Start cell: {start}, End cell: {end}")

map.update_visited_in_occup_grid(pose2, pose1)

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
for row in map.grid[y_min:y_max+1]:
    print(''.join(symbols.get(cell, '?') for cell in row[x_min:x_max+1]))