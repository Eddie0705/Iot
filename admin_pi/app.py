from flask import Flask, render_template, request, redirect, session
from mqtt_admin import publish_announcement
from mqtt_admin import publish_room_status
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))

from database import get_booking_logs, get_usage_logs, get_all_room_status, update_room_status

app = Flask(__name__)
app.secret_key = "admin_secret_key"


def is_logged_in():
    return session.get("admin") is not None


@app.route("/")
def home():
    return render_template("admin_login.html")


@app.route("/login", methods=["POST"])
def login():
    from database import login_user
    email = request.form["email"]
    password = request.form["password"]
    result = login_user(email, password)

    if result.get("success") and result.get("role") == "admin":
        session["admin"] = result["email"]
        return render_template("dashboard.html", user=result["full_name"])

    return render_template("admin_login.html", error="Invalid credentials or not an admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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
    from database import get_all_users
    rows = get_all_users()
    return render_template("users.html", users=rows)


@app.route("/create_staff", methods=["POST"])
def create_staff():
    from database import create_security_staff
    create_security_staff(
        request.form["email"],
        request.form["password"],
        request.form["full_name"],
        request.form["rmit_id"]
    )
    return redirect("/users")


@app.route("/edit_user/<int:user_id>")
def edit_user(user_id):
    from database import get_user_by_id
    user = get_user_by_id(user_id)
    return render_template("edit_user.html", user=user)


@app.route("/update_user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    from database import update_user as db_update_user
    db_update_user(
        user_id,
        request.form["email"],
        request.form["full_name"],
        request.form["role"],
        request.form["status"]
    )
    return redirect("/users")


@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    from database import delete_user as db_delete_user
    db_delete_user(user_id)
    return redirect("/users")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/generate_report")
def generate_report():
    from report_generator import generate_booking_frequency_chart, generate_booking_status_chart
    generate_booking_frequency_chart()
    generate_booking_status_chart()
    return redirect("/reports")


@app.route("/confirm_fault/<int:report_id>", methods=["POST"])
def confirm_fault(report_id):
    from database import resolve_fault_report, get_fault_report_room
    room_name = get_fault_report_room(report_id)
    print(f"confirm_fault: report_id={report_id}, room_name={room_name}")
    if room_name:
        resolve_fault_report(report_id)
        update_room_status(room_name, "fault")
        print(f"confirm_fault: updated {room_name} to fault")
        publish_announcement(f"Room {room_name} down, waiting for maintenance")
    return redirect("/room_status")


@app.route("/room_status")
def room_status():
    from database import get_fault_reports
    rows = get_all_room_status()
    fault_rows = get_fault_reports()
    return render_template("room_status.html", room_status=rows, fault_reports=fault_rows)


@app.route("/update_room", methods=["POST"])
def update_room():
    room = request.form["room"]
    status = request.form["status"]
    update_room_status(room, status)
    publish_room_status(room, status)
    return redirect("/room_status")


app.run(host="0.0.0.0", port=3000, debug=True)
