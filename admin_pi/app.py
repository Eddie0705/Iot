from datetime import datetime

from flask import Flask, render_template, request, redirect
from mqtt_admin import publish_announcement
from mqtt_admin import publish_room_status

app = Flask(__name__)

room_statuses = {
    "A101": "Available",
    "A102": "Occupied",
    "A103": "Maintenance"
}

logs = [
    {
        "type": "Booking Request",
        "room": "A101",
        "message": "Charli requested booking",
        "time": "19:30"
    },

    {
        "type": "Room Status",
        "room": "A102",
        "message": "Room changed to Occupied",
        "time": "19:35"
    },

    {
        "type": "Fault Alert",
        "room": "A103",
        "message": "Projector not working",
        "time": "19:40"
    },

    {
        "type": "Announcement",
        "room": "-",
        "message": "Maintenance scheduled tomorrow",
        "time": "19:45"
    }
]

@app.route("/")
def home():
    return render_template("admin_login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    print(username)

    return render_template("dashboard.html", user=username)

@app.route("/send_announcement", methods=["POST"])
def send_announcement():
    message = request.form["message"]
    result = publish_announcement(message)
    return result


@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/room_status")
def room_status():

    return render_template(
        "room_status.html",
        rooms=room_statuses
    )

@app.route("/update_room", methods=["POST"])
def update_room():

    room = request.form["room"]
    status = request.form["status"]

    room_statuses[room] = status

    logs.append({
    "type": "Room Status",
    "room": room,
    "message": f"{room} changed to {status}",
    "time": datetime.now().strftime("%H:%M")
})
    
    publish_room_status(room, status)

    return redirect("/room_status")

@app.route("/logs")
def logs_page():

    return render_template(
        "logs.html",
        logs=logs
    )

app.run(host="0.0.0.0", port=3000, debug=True)