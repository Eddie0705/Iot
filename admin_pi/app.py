from flask import Flask, render_template, request, redirect
from mqtt_admin import publish_announcement
from mqtt_admin import publish_room_status

app = Flask(__name__)

room_statuses = {
    "A101": "Available",
    "A102": "Occupied",
    "A103": "Maintenance"
}

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

@app.route("/logs")
def logs():
    return render_template("logs.html")

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
    publish_room_status(room, status)

    return redirect("/room_status")

app.run(host="0.0.0.0", port=3000, debug=True)