from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    return f"Received login from {email}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)