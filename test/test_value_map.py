#!/usr/bin/env python3
"""
Test file for ValueMap visualization and update_value_map functionality
"""
import sys
import os
import math

# Add parent directory to path to import occupancy_map
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from occupancy_map import ValueMap, Pose2D

def print_value_numbers(vm, show_range=20):
    """Print actual numeric values from value, conf, and n maps"""
    cx, cy = int(vm.curr_point.x), int(vm.curr_point.y)
    x_min = max(0, cx - show_range)
    x_max = min(vm.map_size_N, cx + show_range)
    y_min = max(0, cy - show_range)
    y_max = min(vm.map_size_N, cy + show_range)
    
    # Value Map - actual numbers
    print(f"\n[VALUE MAP - Numbers] (Drone at [{cx}, {cy}]):")
    for y in reversed(range(y_min, y_max)):
        print(f"{y:5d}:", end="")
        for x in range(x_min, x_max):
            if x == cx and y == cy:
                print(f"     D", end="")  # Mark drone position
            elif vm.n[y, x] > 0:
                print(f"{vm.value[y, x]:6.2f}", end="")
            else:
                print(f"     -", end="")
        print()
    print("       ", end="")
    for x in range(x_min, x_max):
        print(f"{x:6d}", end="")
    print()
    # Confidence Map - actual numbers
    print(f"\n[CONFIDENCE MAP - Numbers]:")
    for y in reversed(range(y_min, y_max)):
        print(f"{y:5d}:", end="")
        for x in range(x_min, x_max):
            if x == cx and y == cy:
                print(f"     D", end="")  # Mark drone position
            elif vm.n[y, x] > 0:
                print(f"{vm.conf[y, x]:6.2f}", end="")
            else:
                print(f"     -", end="")
        print()
    print("       ", end="")
    for x in range(x_min, x_max):
        print(f"{x:6d}", end="")
    print()
    # N Map - actual numbers
    print(f"\n[N MAP - Numbers]:")
    for y in reversed(range(y_min, y_max)):
        print(f"{y:5d}:", end="")
        for x in range(x_min, x_max):
            if x == cx and y == cy:
                print(f"     D", end="")  # Mark drone position
            elif vm.n[y, x] > 0:
                print(f"{vm.n[y, x]:6d}", end="")
            else:
                print(f"     -", end="")
        print()
    print("       ", end="")
    for x in range(x_min, x_max):
        print(f"{x:6d}", end="")
    print()
def test_basic_update():
    """Test basic value map update with single observation"""
    print("=" * 60)
    print("Test 1: Yaw = 0° (facing North)")
    print("=" * 60)
    
    vm = ValueMap(50, 50, 0.1)  # 50m x 50m world, 0.1m cell size
    print(f"Map size: {vm.map_size_N} x {vm.map_size_N} cells")
    print(f"Drone initial position: ({vm.curr_point.x}, {vm.curr_point.y})")
    print(f"Drone yaw: {vm.curr_point.yaw:.2f} rad ({math.degrees(vm.curr_point.yaw):.1f}°) - North")
    
    # Update with a target 30cm forward, 10cm right
    pose = Pose2D(x=30.0, y=10.0, yaw=0.0)  # cm, relative to drone
    vm.update_value_map(0.75, pose, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm, show_range=10)
    
    # Print some statistics
    updated_cells = (vm.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells}")
    print(f"Max value: {vm.value.max():.3f}")
    print(f"Max confidence: {vm.conf.max():.3f}")
    print(f"Max n: {vm.n.max()}")
    '''
    # Test 2: Yaw = 90 degrees (facing East)
    print("\n" + "=" * 60)
    print("Test 2: Yaw = 90° (facing East)")
    print("=" * 60)
    
    vm2 = ValueMap(50, 50, 0.1)
    vm2.curr_point.yaw = math.pi / 2  # 90 degrees
    print(f"Drone yaw: {vm2.curr_point.yaw:.2f} rad ({math.degrees(vm2.curr_point.yaw):.1f}°) - East")
    
    pose2 = Pose2D(x=30.0, y=10.0, yaw=vm2.curr_point.yaw)
    vm2.update_value_map(0.85, pose2, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm2, show_range=10)
    
    updated_cells2 = (vm2.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells2}")
    
    # Test 3: Yaw = 180 degrees (facing South)
    print("\n" + "=" * 60)
    print("Test 3: Yaw = 180° (facing South)")
    print("=" * 60)
    
    vm3 = ValueMap(50, 50, 0.1)
    vm3.curr_point.yaw = math.pi  # 180 degrees
    print(f"Drone yaw: {vm3.curr_point.yaw:.2f} rad ({math.degrees(vm3.curr_point.yaw):.1f}°) - South")
    
    pose3 = Pose2D(x=30.0, y=10.0, yaw=vm3.curr_point.yaw)
    vm3.update_value_map(0.60, pose3, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm3, show_range=10)
    
    updated_cells3 = (vm3.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells3}")
    
    # Test 4: Yaw = -90 degrees / 270 degrees (facing West)
    print("\n" + "=" * 60)
    print("Test 4: Yaw = -90° / 270° (facing West)")
    print("=" * 60)
    
    vm4 = ValueMap(50, 50, 0.1)
    vm4.curr_point.yaw = -math.pi / 2  # -90 degrees = 270 degrees
    print(f"Drone yaw: {vm4.curr_point.yaw:.2f} rad ({math.degrees(vm4.curr_point.yaw):.1f}°) - West")
    
    pose4 = Pose2D(x=30.0, y=10.0, yaw=vm4.curr_point.yaw)
    vm4.update_value_map(0.90, pose4, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm4, show_range=10)
    
    updated_cells4 = (vm4.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells4}")

    # Test 5: Yaw = -90 degrees / 270 degrees (facing NNE)
    print("\n" + "=" * 60)
    print("Test 4: Yaw = -90° / 270° (facing West)")
    print("=" * 60)
    
    vm4 = ValueMap(50, 50, 0.1)
    vm4.curr_point.yaw = math.pi / 8  # 22.5 degrees
    print(f"Drone yaw: {vm4.curr_point.yaw:.2f} rad ({math.degrees(vm4.curr_point.yaw):.1f}°) - NNE")
    
    pose4 = Pose2D(x=30.0, y=10.0, yaw=vm4.curr_point.yaw)
    vm4.update_value_map(0.90, pose4, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm4, show_range=10)
    
    updated_cells4 = (vm4.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells4}")

    # Test 6: Yaw = 45 degrees (facing NE)
    print("\n" + "=" * 60)
    print("Test 4: Yaw = -90° / 270° (facing West)")
    print("=" * 60)
    
    vm4 = ValueMap(50, 50, 0.1)
    vm4.curr_point.yaw = math.pi / 4  # 45 degrees
    print(f"Drone yaw: {vm4.curr_point.yaw:.2f} rad ({math.degrees(vm4.curr_point.yaw):.1f}°) - NE")
    
    pose4 = Pose2D(x=30.0, y=10.0, yaw=vm4.curr_point.yaw)
    vm4.update_value_map(0.90, pose4, fov_deg=82.0, max_range_m=4)
    
    print_value_numbers(vm4, show_range=10)
    
    updated_cells4 = (vm4.n > 0).sum()
    print(f"\nUpdated cells: {updated_cells4}")
    '''
if __name__ == "__main__":
    print("Testing ValueMap update_value_map functionality\n")
    
    test_basic_update()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
