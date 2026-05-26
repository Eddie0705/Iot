import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

import paho.mqtt.client as mqtt
from config import MASTER_HOST

BROKER = MASTER_HOST
PORT = 1883


def on_connect(client, userdata, flags, rc):
    print(f"MQTT subscriber connected (rc={rc})")
    client.subscribe("rooms/+/fault")


def on_message(client, userdata, msg):
    topic = msg.topic
    parts = topic.split("/")
    if len(parts) == 3 and parts[2] == "fault":
        room_name = parts[1]
        print(f"Fault report received for room {room_name} via MQTT")
        from database import report_fault
        result = report_fault(room_name, 1, "Fault reported by Room Pi sensor")
        print(f"Fault report created: {result}")


def start_mqtt_subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        print("MQTT subscriber started")
    except Exception as e:
        print(f"MQTT subscriber failed to connect: {e}")
    return client
