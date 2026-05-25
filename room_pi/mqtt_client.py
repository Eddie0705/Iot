import paho.mqtt.client as mqtt
import time
import json
import secrets

client = mqtt.Client()
BROKER = "INSER.IP.OF.MASTER.PI"


def on_connect(client, userdata, flags, rc):
    client.subscribe("room/response/#") 
    
    global isInitialised
    if not isInitialised:
        global SECRET
        SECRET = secrets.token_hex(32)
        # grab this room pi ID and save it
        client.publish("room/request/", json.dumps({
            "action": "get_room_id",
            "key": SECRET # send room PI back on this ID
        }).encode())

        time.sleep(2) # sleep 2 seconds wait for message to arrive lol
        global ROOMID
        try:
            ROOMID = response["set_room_id"]["id"]
        except: # handle what happens if id is NOT returned or saved or blank
            return

        
        isInitialised = True
    



response = {}
def on_message(client, userdata, msg):
    global response
    global SECRET
    message = json.loads(msg.payload.decode()) # decode to json becasue thats what is sent by master pi
    
    
    action = message.get("action")
    match action: # handle actions

        case "set_room_id":
            print("set_room_id action recieved")

            if SECRET == message.get("key"):
                print("valid key ID")
                response["set_room_id"] = {
                    "id": message.get("id")
                }
            else:
                print("invalid key id")
            
        case "get_booking_status":
            response["get_booking_status"] = {
                #TODO: whatever that is
            }
        case "get_booking_schedule":
            response["get_booking_schedule"] = {
                #TODO:WHATEVER THAT IS
            }
        # IS MORE CASES?!?

        



    return
client.on_connect = on_connect
client.on_message = on_message

#client.connect(BROKER)
#client.loop

