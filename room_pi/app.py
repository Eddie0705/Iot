import sys
import os
import threading
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

import paho.mqtt.publish as mqtt_publish
from config import MASTER_HOST
from flask import Flask, render_template, jsonify, request
from web_data import getWeatherStats, getStatus, getRoomName, getSchedule, ROOM_ID
from socket_client import send_message

app = Flask(__name__)


def auto_checkout_loop():
    while True:
        time.sleep(60)
        bookings = getSchedule()
        from datetime import datetime
        now = datetime.now()
        for b in bookings:
            if b.get("status") == "Checked In":
                end_time = datetime.strptime(b["end_time"], "%Y-%m-%d %H:%M:%S")
                if now >= end_time:
                    send_message({"action": "checkout_room", "room_id": ROOM_ID})
                    break


threading.Thread(target=auto_checkout_loop, daemon=True).start()


@app.route('/')
def home():
    humidity, pressure, temperature = getWeatherStats()
    status = getStatus()
    room_name = getRoomName()
    schedule = getSchedule()
    return render_template(
        "base.html",
        room_name=room_name,
        status=status,
        temperature=round(temperature, 1),
        humidity=round(humidity, 1),
        pressure=round(pressure, 1),
        schedule=schedule
    )


@app.route("/weather-data")
def weather_data():
    humidity, pressure, temperature = getWeatherStats()

    if temperature < 18:
        t_emoji = "Cold"
    elif temperature < 28:
        t_emoji = "Comfortable"
    else:
        t_emoji = "Hot"

    if pressure < 1010:
        p_emoji = "Low"
    elif pressure < 1020:
        p_emoji = "Normal"
    else:
        p_emoji = "High"

    if humidity < 40:
        h_emoji = "Dry"
    elif humidity < 60:
        h_emoji = "Comfortable"
    else:
        h_emoji = "Humid"

    return jsonify({
        "humidity": round(humidity, 1),
        "pressure": round(pressure, 1),
        "temperature": round(temperature, 1),
        "humidityLabel": h_emoji,
        "pressureLabel": p_emoji,
        "temperatureLabel": t_emoji,
    })


@app.route("/booking-status")
def booking_status():
    return jsonify({"status": getStatus()})


@app.route("/schedule")
def schedule():
    return jsonify({"bookings": getSchedule()})


@app.route("/report-fault", methods=["POST"])
def report_fault():
    room_name = getRoomName()
    try:
        mqtt_publish.single(f"rooms/{room_name}/fault", "fault", hostname=MASTER_HOST)
        return jsonify({"status": "success", "message": f"Fault reported for {room_name}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/checkin", methods=["POST"])
def checkin():
    token = request.form.get("token")
    result = send_message({
        "action": "checkin_by_token",
        "room_id": ROOM_ID,
        "token": token
    })
    return jsonify(result)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
