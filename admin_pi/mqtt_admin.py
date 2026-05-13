import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

def publish_announcement(message):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish("admin/announcements", message)
    client.disconnect()

def publish_room_fault(room_id, message):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish(f"rooms/{room_id}/fault", message)
    client.disconnect()