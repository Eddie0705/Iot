import socket
import json


HOST = "10.132.60.32"
PORT = 5050

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
                return json.loads(response_bytes.decode())
            else:
                return {"status": "error", "message": "Server closed connection without responding."}
                
        except ConnectionRefusedError:
            return {"status": "error", "message": f"Connection refused by {HOST}:{PORT}. Is the server running?"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Received invalid JSON from the server."}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
    try:
        ##  Convert the dictionary to a JSON string, then encode it to bytes
        serialized_data = json.dumps(messageJSON).encode()
        
        ##  Send the data to the server
        # Using sendall() ensures all bytes are transmitted
        client_socket.sendall(serialized_data)
        print(f"Sent request: {messageJSON}")
        
        ##  Wait for the server's response (up to 4096 bytes)
        response_bytes = client_socket.recv(4096)
        
        ##  Decode the response back to a string, then parse the JSON
        if response_bytes:
            response_data = json.loads(response_bytes.decode())
            print("Received response from server:")
            print(response_data)
        else:
            print("Server closed connection without sending data.")

    except json.JSONDecodeError:
        print("Error: Received invalid JSON from the server.")
    finally:
        ## 8. Close the socket connection
        client_socket.close()