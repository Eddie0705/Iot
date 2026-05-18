from flask import Flask, render_template, request, redirect
from mqtt_admin import publish_announcement
from mqtt_admin import publish_room_status
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))

from db_setup import get_connection
from database import get_booking_logs, get_usage_logs, get_all_room_status


app = Flask(__name__)

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


@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/room_status")
def room_status():
    room_status = get_all_room_status()
    return render_template("room_status.html", room_status=room_status)

@app.route("/update_room", methods=["POST"])
def update_room():

    room = request.form["room"]
    status = request.form["status"]

    publish_room_status(room, status)

    return redirect("/room_status")

app.run(host="0.0.0.0", port=3000, debug=True)