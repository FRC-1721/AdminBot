import os
import sys
import time
import random
import logging
import threading


from flask import Flask, render_template, jsonify, request

from flask_socketio import SocketIO

from threading import Lock

from datetime import datetime, timedelta

from tools.misc import getVersion, getNextMeeting


# Thread locking
thread = None
thread_lock = Lock()

# Configure Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = "frc1721!"
socketio = SocketIO(app, cors_allowed_origins="*")

# App Memory
discord_logs = [
    ["dublU", "First!", "General", 1692832019],
    ["KenwoodFox", "How does he do it every time?!", "General", 1692832030],
]
max_discord_logs = 30


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


@app.route("/dashboard/hook", methods=["POST"])
def webhook():
    if request.method == "POST":
        logging.debug(
            f"Data received from Webhook is: {request.data} data was {request.json}"
        )

        data = request.json
        discord_logs.append(
            [data["author"], data["content"], data["channel"], int(time.time())]
        )

        while len(discord_logs) > max_discord_logs:
            discord_logs.pop(0)

        return "Webhook processed!"


# Generate random sequence of dummy sensor values and send it to our clients
def websocket_push():
    while True:
        data = {
            "version": getVersion(),
            "date": get_current_datetime(),
            "discord": discord_logs,
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
