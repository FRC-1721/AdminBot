import sys
import time
import random
import threading

from flask import Flask, render_template, jsonify

from datetime import datetime, timedelta

import consts

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_time")
def get_time():
    now = datetime.now()
    epoch = datetime.fromtimestamp(consts.MISSION_EPOCH)

    missionTime = now - epoch

    data = {"t": f"T+{str(missionTime).split('.')[0]}", "name": "Countdown to Kickoff"}
    return jsonify(data)
