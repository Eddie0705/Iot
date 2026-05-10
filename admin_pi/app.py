from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("admin_login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    print(username)

    return render_template("dashboard.html", user=username)

app.run(host="0.0.0.0", port=5000, debug=True)