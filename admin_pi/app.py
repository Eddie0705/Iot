from flask import Flask, render_template, request
from mqtt_admin import publish_announcement

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
    return render_template("room_status.html")

app.run(host="0.0.0.0", port=3000, debug=True)