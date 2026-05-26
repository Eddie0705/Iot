import paho.mqtt.client as mqtt
import sys
import os
import threading
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config import MASTER_HOST

BROKER = MASTER_HOST
PORT = 1883

security_alerts = []

try:
    from sense_hat import SenseHat
    sense = SenseHat()
    SENSE_AVAILABLE = True
except Exception:
    sense = None
    SENSE_AVAILABLE = False


def trigger_fault_alert():
    if not SENSE_AVAILABLE:
        print("Sense HAT not available — skipping visual alert")
        return

    red = (255, 0, 0)
    off = (0, 0, 0)

    # Flash red 5 times
    for _ in range(5):
        sense.clear(red)
        time.sleep(0.5)
        sense.clear(off)
        time.sleep(0.5)

    # Show warning X in red
    sense.show_message("FAULT", text_colour=red, scroll_speed=0.08)
    sense.clear()


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

    # Trigger Sense HAT alert if room status is fault
    if "status" in msg.topic and alert_message.lower() == "fault":
        threading.Thread(target=trigger_fault_alert, daemon=True).start()


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