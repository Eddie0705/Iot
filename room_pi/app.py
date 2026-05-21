import sense_emu as SenseHat

import time

# from ..common.config import *
import paho.mqtt.client as mqtt

from flask import Flask, render_template, request, jsonify


# s = SenseHat()
client = mqtt.Client()
BROKER = "INSERT.IP" # FIND THAT IP
subscribeTopics = [
    # empty cos we add the responses as we go on
    # reponses.append("reponse/XXXX")
    # on client connect to broker appends all responses and listens to them
]
client.connect(BROKER)
client.loop_start()
response = {}


def on_message(client, userdata, msg):
    global response
    topic = msg.topic
    message = msg.payload.decode()

    if topic not in response:
        response[topic] = []

    response[topic].append(message) # query topic and most recent array for newest values


def on_connect(client, userdata, flags, rc):
    for i in subscribeTopics:
        client.subscribe(i)

client.on_connect = on_connect
client.on_message = on_message


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
    with "request/bookings" as REQUEST:
        client.publish(REQUEST, "INSERT REQUEST STRING HERE")
    
    RESPONSE = "response/bookings"
    if RESPONSE not in subscribeTopics:
        subscribeTopics.append(RESPONSE)

    # Publish Request
    time.sleep(2) # Wait for response
    
    if (response[RESPONSE][-1].lower() == "false"):
        return False
    elif (response[RESPONSE][-1].lower() == "true"):
        return True
    else:
        raise TypeError(f"This topic does not return a valid result, {RESPONSE=}, {response[RESPONSE][-1].lower()=}")

def getSchedule() -> list[list[str]]:
    REQUEST = "request/bookings"
    RESPONSE = "response/bookings"
    if RESPONSE not in subscribeTopics:
        subscribeTopics.append(RESPONSE)

    client.publish(REQUEST, "INSERT REQUEST STRING HERE")
    time.sleep(2)
    response[RESPONSE][-1] # response result
    
    return None

app.run(debug=True)

#commented out because sense-emu is kinda broken rn though no reason it wouldnt work on a real pi remember to change import
def getStats() -> tuple[float, float, float]:
    humidity = s.get_humidity()
    pressure = s.get_pressure()
    temperature = s.get_temperature()

    return (humidity, pressure, temperature)






