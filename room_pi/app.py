import sense_emu as SenseHat

import time

# from ..common.config import *
import paho.mqtt.client as mqtt

from flask import Flask, render_template, request


s = SenseHat()
client = mqtt.Client()
KEEPALIVE = 60 # how long to keep the connection Alive in seconds

#client.connect(MASTER_IP, MASTER_PORT, KEEPALIVE)

app = Flask(__name__)

@app.route('/')
def home():
    # render homepage Header basically
    return render_template("base.html")

@app.route('/weather')
def weatherUpdates():
    # Renders index.html from the templates folder
    humidity, pressure, temperature = getStats()
    return render_template('weather.html', humidity=humidity, pressure=pressure, temperature=temperature)

@app.route('/booking')
def bookingStatusNow():
    isBookedNow: bool = False # source this function elsewhere
    if (isBookedNow):
        return render_template('booking.html', BookedNow="myb 5 no space")
    else: return render_template('booking.html', BookedNow="Slide thru Slime!")

#commented out because sense-emu is kinda broken rn though no reason it wouldnt work

def getStats() -> tuple[float, float, float]:
    humidity = s.get_humidity()
    pressure = s.get_pressure()
    temperature = s.get_temperature()

    return (humidity, pressure, temperature)


app.run(debug=True)


