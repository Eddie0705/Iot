import paho.mqtt.client as mqtt
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config import MASTER_HOST

BROKER = MASTER_HOST
PORT = 1883

security_alerts = []


# Connect to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Agent Pi connected to MQTT broker")
        client.subscribe("admin/announcements")
        client.subscribe("rooms/+/status")
        print("Subscribed successfully")
    else:
        print("MQTT connection failed")


# Receive MQTT messages
def on_message(client, userdata, msg):
    alert_message = msg.payload.decode()
    print("MQTT alert received:", alert_message)

    security_alerts.insert(0, alert_message)

    if len(security_alerts) > 5:
        security_alerts.pop()


# Start subscriber in background
def start_subscriber():
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(BROKER, PORT, 60)
        client.loop_start()

    except Exception as e:
        print("MQTT unavailable:", e)