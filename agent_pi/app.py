from flask import Flask, render_template, request
from client import send_request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    message = {
        "action": "login",
        "email": email,
        "password": password
    }

    response = send_request(message)

    return render_template("login.html", response=response)

@app.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        message = {
            "action": "register",
            "full_name": full_name,
            "email": email,
            "password": password
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

    # when user submits booking form
    if request.method == "POST":

        room_id = request.form["room_id"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        # create request message for Master Pi
        request_data = {
            "action": "book_room",
            "room_id": room_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }

        # send request through socket
        response = send_request(request_data)

        return render_template("book.html", response=response)

    # open booking page
    return render_template("book.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)