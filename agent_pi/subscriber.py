import paho.mqtt.client as mqtt

BROKER = "10.132.66.24"
PORT = 1883
## this runs when Agent Pi connects to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Agent Pi connected to MQTT broker")
        client.subscribe("admin/announcements")
        client.subscribe("rooms/+/status")
        print("Subscribed to admin/announcements and rooms/+/status")
    else:
        print("Connection failed")


## this runs when Agent Pi receives an alert
def on_message(client, userdata, msg):
    alert_message = msg.payload.decode()
    print("MQTT alert received:", alert_message)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

print("Waiting for MQTT alerts...")
client.loop_forever()