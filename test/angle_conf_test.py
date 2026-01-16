import numpy as np
import matplotlib.pyplot as plt
import math
import os

def angle_confidence(theta: float, fov_rad: float) -> float:
    half = fov_rad / 2.0
    if half <= 1e-9:
        return 0.0
    t = abs(theta) / half
    if t >= 1.0:
        return 0.0
    return (math.cos(t * (math.pi / 2.0)) ** 2)

fov_deg = 82.0
fov_rad = math.radians(fov_deg)
half_deg = fov_deg / 2.0

theta_deg = np.linspace(-half_deg, half_deg, 400)
theta_rad = np.radians(theta_deg)
print(theta_rad)
conf = np.array([angle_confidence(t, fov_rad) for t in theta_rad])

plt.figure()
plt.plot(theta_deg, conf)
plt.xlabel("Relative angle θ (degrees)")
plt.ylabel("Confidence c(θ)")
plt.title(f"Angle-based confidence: cos^2 profile (FOV = {fov_deg}°)")
plt.grid(True)
plt.ylim(-0.05, 1.05)
plt.xlim(-half_deg, half_deg)

# try show; if no display, save instead
if os.environ.get("DISPLAY") is None and os.name != "nt":
    plt.savefig("conf_plot.png", dpi=200)
    print("No DISPLAY found. Saved plot to conf_plot.png")
else:
    plt.show(block=True)
