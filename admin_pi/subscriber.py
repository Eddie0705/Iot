import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message}")

client = mqtt.Client()

client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.subscribe("admin/announcements")

print("Listening for announcements...")

client.loop_forever()