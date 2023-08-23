import os
import sys
import time
import random
import logging
import threading


from flask import Flask, render_template, jsonify, request

from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from threading import Lock

from datetime import datetime, timedelta

from tools.misc import getVersion, getNextMeeting

from shared.models import db, DiscordMessage


# Thread locking
thread = None
thread_lock = Lock()

# Configure Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = "frc1721!"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://postgres:postgres@database/admin_bot_db"
socketio = SocketIO(app, cors_allowed_origins="*")

# Connect/init DB
db.init_app(app)

# Create app tables
with app.app_context():
    logging.info("Applying initial DB creation setup.")
    db.create_all()


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
        discord_logs = []
        with app.app_context():
            for line in DiscordMessage.query.all():
                discord_logs.append(
                    [line.username, line.content, line.channel, line.time]
                )

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
