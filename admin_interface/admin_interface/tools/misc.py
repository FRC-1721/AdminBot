# Misc tools

import os
import string
import random


def get_uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])

    return uptime_seconds


def getVersion():
    """
    Returns the current app version (or a random one if in debug mode)
    """

    ret = str(os.environ.get("GIT_COMMIT"))
    if ret == "None":
        os.environ["GIT_COMMIT"] = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=7)
        )
    return str(os.environ.get("GIT_COMMIT"))
