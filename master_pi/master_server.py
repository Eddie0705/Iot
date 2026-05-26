import socket
import json
# schedule of user booking (need time of booking) + confirmation of check in 
from database import (
    login_user,
    get_booking_logs,
    get_usage_logs,
    get_booking_history,
    get_all_room_status,
    update_room_status,
    get_all_users,
    get_fault_reports,
    resolve_fault_report,
    create_security_staff,
    update_user,
    delete_user,
    get_user_by_id,
    register_user,
    search_room,
    book_room,
    cancel_booking,
    use_room,
    return_room
)

HOST = "0.0.0.0"
PORT = 5050


def combine_datetime(date, time):
    return f"{date} {time}:00"

def handle_request(request):
    action = request.get("action")

    if action == "ping":
        return {
            "status": "success",
            "message": "Master Pi server is running"
        }

    if action == "login":
        return login_user(
            request.get("email"),
            request.get("password")
        )
    if action == "register":
        return register_user(
            request.get("email"),
            request.get("password"),
            request.get("full_name"),
            request.get("rmit_id")
        )

    if action == "search_room":
        start_datetime = combine_datetime(
            request.get("date"),
            request.get("start_time")
        )

        end_datetime = combine_datetime(
            request.get("date"),
            request.get("end_time")
        )

        return search_room(
            start_datetime,
            end_datetime
        )

    if action == "book_room":
        start_datetime = combine_datetime(
            request.get("date"),
            request.get("start_time")
        )

        end_datetime = combine_datetime(
            request.get("date"),
            request.get("end_time")
        )

        return book_room(
            request.get("room_id"),
            start_datetime,
            end_datetime,
            request.get("user_id", 1)
        )

    if action == "cancel_booking":
        return cancel_booking(
            request.get("booking_id"),
            request.get("user_id", 1)
        )

    if action == "use_room":
        return use_room(
            request.get("booking_id"),
            request.get("room_id"),
            request.get("token")
        )

    if action == "return_room":
        return return_room(
            request.get("booking_id"),
            request.get("room_id")
        )
        
    else:
        return {
            "status": "error",
            "message": "Unknown action"
        }


def start_server():
    ## create TCP socket server using IPv4 addresses/socket.AF_INET and TCP protocol/socket.SOCK_STREAM
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ## allow the socket to reuse the port quickly after restarting the server
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ## run server on 0.0.0.0 and port 5050
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

        ## receive data from client up to 4096 bytes and then decode it from bytes to string/normal text
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