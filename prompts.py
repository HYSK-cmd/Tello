nav_prompt_system = \
"""
You are controlling a UAV flying in an environment. Your task is to navigate the UAV safely to a specified destination while avoiding obstacles such as buildings, trees, and other aerial vehicles. You will receive real-time visual input from the UAV's front camera and must make decisions based on this input.
"""

nav_target_desc = \
"""
Target description:
The target is the person holding the red umbrella.

Target surrounding description: 
The person with the red umbrella is standing on open ground near a historical-style building. Several other pedestrians are walking nearby.
"""

nav_vanilla_ask = \
"""
Based on the visual input, decide a single control command for the UAV to move closer to the target while ensuring safety and efficiency.

If distance_to_target <= 10 (centimeters), you must output "stop".

Output format (MUST follow exactly):
- For translation (cm): "move_forward D", "move_backward D", "move_left D", "move_right D", "move_up D", or "move_down D"
  - D is a positive integer distance in centimeters
- For rotation (degrees): "turn_cw A" or "turn_ccw A"
  - A is a positive integer angle in degrees where 0 < A < 360.
- For no movement: "hover"
- For stopping due to proximity: "stop"

Rules:
- Output EXACTLY ONE command in ONE line.
- Do NOT add any extra words, punctuation, units, or explanation.
"""

nav_prompt_vanilla = nav_prompt_system + "\n" + nav_target_desc + "\n" + nav_vanilla_ask