from flask import Flask, render_template, request, jsonify

from room_pi.web_data import *

app = Flask(__name__)

@app.route('/')
def home():
    # render homepage basically
    return render_template("base.html")

# for javacript refreshes
@app.route("/weather-data")
def weatherData():

    humidity, pressure, temperature = (20, 1, 3)
    # getWeatherStats()
    
    # Temperature Emojis
    # this genuinely the code equivelent of a colouring book bruh 
    if (temperature < 18): tMoji = "🥶"
    elif (temperature < 28): tMoji = "😁"
    else: tMoji = "🥵"

    if (pressure < 1010): pMoji = "🌵"
    elif (pressure < 1020): pMoji = "🌿"
    else: pMoji = "💦"


    if (humidity < 40): hMoji = "🍃"
    elif (humidity < 60): hMoji = "☁️"
    else: hMoji = "🥵"

    return jsonify(
        {"humidity": humidity, "pressure": pressure, "temperature": temperature,
         "humidityEmoji": hMoji, "pressureEmoji": pMoji, "temperatureEmoji": tMoji, }
    )

@app.route("/booking-data")
def bookingUpdates():
     # define this function
    if (True):
        return jsonify(
            {"status": "Yea this room is Booked right now, Sorry lol"}
        )
    else:
        return jsonify(
            {"status": "Slide through, this room is free"}
        )
















