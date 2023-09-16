# Manages getting and showing promo images

import time
import json
import logging

from os import listdir, remove
from os.path import isfile, join


promo_path = "static/promo/"
current_index = 0
valid_promos = []
last_run = 0
time_per_image = 25  # Seconds

placeholderImg = "static/placeholder/default.png"


def getNextImage(prune=True) -> tuple:
    global current_index
    global valid_promos
    global last_run
    global placeholderImg

    try:
        files = [f for f in listdir(promo_path) if isfile(join(promo_path, f))]
    except FileNotFoundError:
        logging.debug("Not running in prod environment or docker volume missing.")
        return placeholderImg, None

    _now = int(time.time())

    if last_run + time_per_image < _now:
        last_run = _now
        valid_promos = []  # Clear valid promo's

        for file in files:
            if ".png" in file:
                fname = file.split(".")[0]
                if isfile(join(promo_path, f"{fname}.json")):
                    fdata = json.load(open(join(promo_path, f"{fname}.json")))
                    logging.debug(f"Loaded file with metadata {fdata}")

                    if int(fdata["expires"]) < int(time.time() and prune):
                        logging.info("Pruning image file with expired date")
                        remove(join(promo_path, file))
                        remove(join(promo_path, f"{fname}.json"))
                    else:
                        # Its valid!
                        logging.debug(f"Added {file} to valid promo's list")

                        _caption = fdata["caption"]
                        valid_promos.append([file, _caption])
                else:
                    logging.warn("Pruning image file with no matching json")
                    remove(join(promo_path, file))

        current_index += 1

        if len(valid_promos) - 1 < current_index:
            current_index = 0

    if len(valid_promos) == 0:
        logging.debug("Nothing in rotation, showing default")
        return placeholderImg, None

    logging.debug("No need to update image yet.")
    _promo_path = f"static/promo/{valid_promos[current_index][0]}"

    return _promo_path, valid_promos[current_index][1]
