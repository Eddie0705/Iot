import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "group37/alerts"


## this runs when Agent Pi connects to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Agent Pi connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}")
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