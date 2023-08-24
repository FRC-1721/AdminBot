# Manages getting and showing promo images

import time
import json
import logging

from os import listdir, remove
from os.path import isfile, join


promo_path = "static/promo/"
current_index = 0
valid_promos = []
time_per_image = 4  # Seconds


def getNextImage(prune=True):
    files = [f for f in listdir(promo_path) if isfile(join(promo_path, f))]

    global current_index
    global valid_promos

    if int(time.time()) % time_per_image == 0:
        valid_promos = []

        for file in files:
            if ".png" in file:
                fname = file.split(".")[0]
                if isfile(join(promo_path, f"{fname}.json")):
                    fdata = json.load(open(join(promo_path, f"{fname}.json")))
                    logging.debug(f"Loaded file with metadata {fdata}")

                    if int(fdata["expires"]) < int(time.time()):
                        logging.info("Pruning image file with expired date")
                        remove(join(promo_path, file))
                        remove(join(promo_path, f"{fname}.json"))
                    else:
                        # Its valid!
                        logging.debug(f"Added {file} to valid promo's list")
                        valid_promos.append(file)
                else:
                    logging.info("Pruning image file with no matching json")
                    remove(join(promo_path, file))

        current_index += 1

    if len(valid_promos) > 0:
        if len(valid_promos) - 1 < current_index:
            current_index = 0
        return f"static/promo/{valid_promos[current_index]}"
    else:
        return "static/placeholder/320x240.png"
