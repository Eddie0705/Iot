import paho.mqtt.client as mqtt

# BROKER = "localhost"
#conection to the master pi mqtt broker
BROKER = "10.132.66.24"
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