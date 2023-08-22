import os
import sys
import time
import random
import logging
import threading


from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

from random import random
from threading import Lock

from datetime import datetime, timedelta

from tools.misc import getVersion


thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "frc1721!"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("index.html", version=getVersion())


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", version=getVersion())


# Get current date time
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


# Generate random sequence of dummy sensor values and send it to our clients
def background_thread():
    while True:
        data = {
            "version": getVersion(),
            "date": get_current_datetime(),
            "idk": "Hello World",
        }

        socketio.emit("updateSensorData", data)
        socketio.sleep(1)


# Client Connect
@socketio.on("connect")
def connect():
    global thread
    logging.info("Client connected")

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


# Client Disconnect
@socketio.on("disconnect")
def disconnect():
    logging.info("Client disconnected", request.sid)


@app.route("/get_time")
def get_time():
    now = datetime.now()
    epoch = datetime.fromtimestamp(consts.MISSION_EPOCH)

    missionTime = now - epoch

    data = {"t": f"T+{str(missionTime).split('.')[0]}", "name": "Countdown to Kickoff"}
    return jsonify(data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    socketio.run(app)
