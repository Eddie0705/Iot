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



response = {}
def on_message(client, userdata, msg):
    global response
    try:
        message = json.loads(msg.payload.decode()) # decode to json becasue thats what is sent by master pi
    except Exception as e:
        print("Error Decoding Request")
        print(e)
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
            global ROOMID
            ROOMID = None
            if (ROOMID == None):
                serialized_data = json.dumps({"action": "get_room_id"}).encode()
                client_socket.sendall(serialized_data)
                response_bytes = client_socket.recv(4096)
                if response_bytes:
                    ROOMID = json.loads(response_bytes.decode()["room_id"])
                else:
                    print("error getting room ID")
                    return
            else:
                message_data["room_id"] = ROOMID

            # Serialize and send the data
            serialized_data = json.dumps(message_data).encode()
            client_socket.sendall(serialized_data)
            
            # Receive the response
            response_bytes = client_socket.recv(4096)
            
            # Parse and return the response
            if response_bytes:
                handleMessage(json.loads(response_bytes.decode()))
                return json.loads(response_bytes.decode())
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

        response
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