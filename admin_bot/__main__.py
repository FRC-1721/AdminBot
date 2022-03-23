# Tidal Force Robotics
# 2021, Email Blaster
# MIT License

import os
import time


print("Hello world!")

version = str(os.environ.get("GIT_COMMIT"))

print(f"Version {version}")


while True:
    time.sleep(10)
