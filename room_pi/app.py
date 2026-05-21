import sense_emu as SenseHat

import time

# from ..common.config import *
import paho.mqtt.client as mqtt

from flask import Flask, render_template, request, jsonify


# s = SenseHat()
client = mqtt.Client()
KEEPALIVE = 60 # how long to keep the connection Alive in seconds

#client.connect(MASTER_IP, MASTER_PORT, KEEPALIVE)

app = Flask(__name__)

@app.route('/')
def home():
    # render homepage basically
    return render_template("base.html")

# for javacript refreshes
@app.route("/weather-data")
def weatherData():
    humidity, pressure, temperature = (67, 1, 3)  # getStats()
    return jsonify(
        {"humidity": humidity, "pressure": pressure, "temperature": temperature}
    )



@app.route('/booking')
def bookingStatusNow():
    isBookedNow: bool = False # source this function elsewhere
    if (isBookedNow):
        return render_template('booking.html', BookedNow="myb 5 no space")
    else: return render_template('booking.html', BookedNow="Slide thru Slime!")

@app.route("/booking-data")
def bookingUpdates():
     # define this function
    if (isBooked()):
        return jsonify(
            {"status": "Yea this room is Booked right now, Sorry lol"}
        )
    else:
        return jsonify(
            {"status": "Slide through, this room is free"}
        )


def isBooked() -> bool:
    #some function to determine if room is booked rn, figure out based on Database

    return False


app.run(debug=True)

#commented out because sense-emu is kinda broken rn though no reason it wouldnt work on a real pi remember to change import
def getStats() -> tuple[float, float, float]:
    humidity = s.get_humidity()
    pressure = s.get_pressure()
    temperature = s.get_temperature()

    return (humidity, pressure, temperature)





