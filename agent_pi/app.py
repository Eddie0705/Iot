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

@app.route("/search")
def search_page():
    return render_template("search.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)