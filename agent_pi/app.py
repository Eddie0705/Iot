from flask import Flask, render_template, request, redirect, url_for, session
from client import send_request
from qr_service import generate_qr_base64

app = Flask(__name__)
app.secret_key = "agent_secret_key"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        request_data = {
            "action": "login",
            "email": request.form["email"],
            "password": request.form["password"]
        }

        response = send_request(request_data)

        if response.get("status") == "success":
            session["user_id"] = response.get("user_id")
            session["email"] = response.get("email")
            return redirect(url_for("dashboard"))

        return render_template("login.html", response=response)

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        rmit_id = request.form.get("rmit_id")

        message = {
            "action": "register",
            "full_name": full_name,
            "email": email,
            "password": password,
            "rmit_id": rmit_id
        }

        response = send_request(message)

        return render_template("register.html", response=response)

    return render_template("register.html")

@app.route("/search", methods=["GET", "POST"])
def search_page():
    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        message = {
            "action": "search_room",
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }

        response = send_request(message)

        return render_template("search.html", response=response)

    return render_template("search.html")

@app.route("/book", methods=["GET", "POST"])
def book_room():

    if request.method == "POST":
        room_id = request.form["room_id"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        request_data = {
            "action": "book_room",
            "room_id": room_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "user_id": session.get("user_id", 1)
        }

        response = send_request(request_data)

        qr_code = None
        if response.get("status") == "success":
            qr_code = generate_qr_base64(response["booking_id"], response["token"])

        return render_template("book.html", response=response, qr_code=qr_code)

    return render_template("book.html")

@app.route("/cancel", methods=["GET", "POST"])
def cancel_booking():
    ## when user submits the cancellation form
    if request.method == "POST":
        ## get booking id entered by user
        booking_id = request.form["booking_id"]

        ## create request data to send to Master Pi
        request_data = {
            "action": "cancel_booking",
            "booking_id": booking_id,
            "user_id": session.get("user_id", 1)
        }

        ## send request to Master Pi and get response
        response = send_request(request_data)

        ## show response back on cancel page
        return render_template("cancel.html", response=response)

    ## open cancel booking page
    return render_template("cancel.html")

@app.route("/room-use", methods=["GET", "POST"])
def room_use():

    ## when user submits the form
    if request.method == "POST":

        ## get form data entered by user
        booking_id = request.form["booking_id"]
        room_id = request.form["room_id"]
        room_action = request.form["room_action"]

        ## create request data for Master Pi
        request_data = {
            "action": room_action,
            "booking_id": booking_id,
            "room_id": room_id,
            "token": request.form.get("token", ""),
            "user_id": session.get("user_id", 1)
        }

        ## send request and get response
        response = send_request(request_data)

        ## show response back on webpage
        return render_template("room_use.html", response=response)

    ## open room use page
    return render_template("room_use.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)