import socket
import json

HOST = "0.0.0.0"
PORT = 5050


def handle_request(request):
    action = request.get("action")

    if action == "ping":
        return {
            "status": "success",
            "message": "Master Pi server is running"
        }

    if action == "login":
        return {
            "status": "success",
            "message": "Login request received by Master Pi"
        }

    if action == "register":
        return {
            "status": "success",
            "message": "Registration request received by Master Pi"
        }

    if action == "search_room":
        return {
            "status": "success",
            "message": "Room search request received by Master Pi"
        }
    
    if action == "book_room":
        return {
            "status": "success",
            "message": "Booking request received by Master Pi"
        }
        
        return {
            "status": "error",
            "message": "Unknown action"
        }


def start_server():
    ## create TCP socket server using IPv4 addresses/socket.AF_INET and TCP protocol/socket.SOCK_STREAM
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ## run server on 0.0.0.0 and port 5000
    server_socket.bind((HOST, PORT))
    ## start listening for client to connect
    server_socket.listen()

    print("Master Pi socket server is running...")
    print(f"Listening on port {PORT}")

    while True:
        ## wait for client to connect
        # store client socket connection
        # and client address, which is its IP address and port number
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        ## receive data from client up to 4065 bytes and then decode it from bytes to string/normal text
        data = client_socket.recv(4096).decode()

        try:
            request = json.loads(data)
            print("Received request:", request)
            response = handle_request(request)

        except json.JSONDecodeError:
            response = {
                "status": "error",
                "message": "Invalid JSON format"
            }

        ## send response back to client, convert it into JSON text and then into bytes before sending
        client_socket.send(json.dumps(response).encode())
        client_socket.close()


if __name__ == "__main__":
    start_server()