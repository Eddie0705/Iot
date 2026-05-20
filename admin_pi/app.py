from datetime import datetime
from flask import Flask, render_template, request, redirect
from mqtt_admin import publish_announcement
from mqtt_admin import publish_room_status
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))

from db_setup import get_connection
from database import get_booking_logs, get_usage_logs, get_all_room_status, update_room_status


app = Flask(__name__)

room_statuses = {
    "A101": "Available",
    "A102": "Occupied",
    "A103": "Maintenance"
}


fault_reports = [
    {
        "room": "A204",
        "issue": "Projector broken",
        "status": "Fault"
    },

    {
        "room": "A102",
        "issue": "Air conditioning failure",
        "status": "Fault"
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
    publish_announcement(message)
    return redirect("/")


@app.route("/logs")
def logs():
    booking_rows = get_booking_logs()
    usage_rows = get_usage_logs()
    return render_template("logs.html", booking_logs=booking_rows, usage_logs=usage_rows)

@app.route("/users")
def users():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT user_id, email, full_name, rmit_id, role, status FROM users")
    users = cur.fetchall()
    con.close()
    return render_template("users.html", users=users)

@app.route("/room_status")
def room_status():
    room_status = get_all_room_status()
    return render_template("room_status.html", room_status=room_status)

@app.route("/update_room", methods=["POST"])
def update_room():

    room = request.form["room"]
    status = request.form["status"]

    update_room_status(room, status)
    publish_room_status(room, status)

    return redirect("/room_status")


@app.route("/reports")
def reports():

    return render_template(
        "reports.html",
        fault_reports=fault_reports
    )

@app.route("/users")
def users_page():

    return render_template(
        "users.html",
        users=users
    )

@app.route("/confirm_fault/<room>")
def confirm_fault(room):

    room_statuses[room] = "Under Maintenance"

    for report in fault_reports:

        if report["room"] == room:
            report["status"] = "Under Maintenance"

    publish_announcement(
        f"Room {room} down, waiting for maintenance"
    )

    logs.append({
        "type": "Fault Decision",
        "room": room,
        "message": f"{room} waiting for maintenance",
        "time": datetime.now().strftime("%H:%M")
    })

    return redirect("/reports")

app.run(host="0.0.0.0", port=3000, debug=True)