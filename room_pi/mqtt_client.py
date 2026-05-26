import paho.mqtt.client as mqtt
import time
import json
import secrets
import socket

client = mqtt.Client()
BROKER = "10.132.60.32" # FIX IP

HOST = "10.132.60.32"
PORT = 5050

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
        except: 
            # TODO: handle what happens if id is NOT returned or saved or blank
            return

        
        isInitialised = True
    



response = {}
def on_message(client, userdata, msg):
    global response
    global SECRET
    message = json.loads(msg.payload.decode()) # decode to json becasue thats what is sent by master pi
    handleMessage(message)



def send_message(message_data):
    """
    Connects to a TCP socket server, sends a JSON-encoded message,
    waits for a response, and returns it.
    """
    # Using 'with' ensures the socket is automatically closed when the block ends
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server
            client_socket.connect((HOST, PORT))
            
            # Serialize and send the data
            serialized_data = json.dumps(message_data).encode()
            client_socket.sendall(serialized_data)
            
            # Receive the response
            response_bytes = client_socket.recv(4096)
            
            # Parse and return the response
            if response_bytes:
                handleMessage(json.loads(response_bytes.decode()))
                return
            else:
                return {"status": "error", "message": "Server closed connection without responding."}
                
        except ConnectionRefusedError:
            return {"status": "error", "message": f"Connection refused by {HOST}:{PORT}. Is the server running?"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Received invalid JSON from the server."}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def handleMessage(message):
    try:
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

            case "get_room_status":

                print("Updates Room Status")
                response["get_room_status"] = {
                    "status": message.get("status")
                }            
            case "get_room_schedule":

                response["get_room_schedule"] = {
                    #TODO: whatever that is
                }



            case "get_booking_schedule":
                response["get_booking_schedule"] = {
                    #TODO:WHATEVER THAT IS
                }
            case _: # default case
                print(f"Action not found: {action=}")
    except Exception as e:
        print("somethign went wrong. 😁")
        print(f"{action=}")
        print(e)
        # IS MORE CASES?!? 


client.on_connect = on_connect
client.on_message = on_message

#client.connect(BROKER)
#client.loop

