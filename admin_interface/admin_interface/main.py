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

from tools.misc import getVersion, getNextMeeting


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
def websocket_push():
    while True:
        data = {
            "version": getVersion(),
            "date": get_current_datetime(),
            "discord": [
                ["KenwoodFox", "I'm joe.", "Software", 1692797080],
                ["dublU", "Joe momma", "Software", 1692797082],
            ],
            "next_meeting": getNextMeeting(),
            "promo_path": "static/placeholder/example1.png"
            if int(time.time()) % 20 >= 10
            else "static/placeholder/example2.png",
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
            thread = socketio.start_background_task(websocket_push)


# Client Disconnect
@socketio.on("disconnect")
def disconnect():
    logging.info("Client disconnected", request.sid)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        handlers=[
            logging.FileHandler("/tmp/admin_interface.log"),
            logging.StreamHandler(),
        ],
    )
    socketio.run(app)
