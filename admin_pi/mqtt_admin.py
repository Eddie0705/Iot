import paho.mqtt.client as mqtt
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config import MASTER_HOST

BROKER = MASTER_HOST
PORT = 1883

def publish_announcement(message):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish("admin/announcements", message)
    client.disconnect()

def publish_room_status(room_id, message):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish(f"rooms/{room_id}/status", message)
    client.disconnect()