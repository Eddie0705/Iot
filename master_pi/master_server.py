import socket
import json
from db_setup import get_connection
import random
import string

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
        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                SELECT user_id, email, full_name, role
                FROM users
                WHERE email = %s
                AND password = %s
                AND status = 'active'
            """, (
                request.get("email"),
                request.get("password")
            ))

            user = cur.fetchone()
            con.close()

            if user:
                return {
                    "status": "success",
                    "message": "Login successful",
                    "user_id": user[0],
                    "email": user[1],
                    "full_name": user[2],
                    "role": user[3]
                }

            return {
                "status": "error",
                "message": "Invalid email or password"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Login failed: {e}"
            }

    if action == "register":
        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                INSERT INTO users (email, password, full_name, rmit_id, role, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                request.get("email"),
                request.get("password"),
                request.get("full_name"),
                request.get("rmit_id"),
                request.get("role", "user"),
                "active"
            ))

            con.commit()
            con.close()

            return {
                "status": "success",
                "message": "User registered successfully"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Registration failed: {e}"
            }

    if action == "search_room":
        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                SELECT room_id, room_name, location, capacity, status
                FROM rooms
                WHERE status = 'available'
            """)

            rooms = cur.fetchall()
            con.close()

            room_list = []
            for room in rooms:
                room_list.append({
                    "room_id": room[0],
                    "room_name": room[1],
                    "location": room[2],
                    "capacity": room[3],
                    "status": room[4]
                })

            return {
                "status": "success",
                "message": "Available rooms found",
                "rooms": room_list
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    if action == "book_room":
        try:
            token = "TOKEN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            room_id = request.get("room_id")
            date = request.get("date")
            start_time = request.get("start_time")
            end_time = request.get("end_time")

            start_datetime = f"{date} {start_time}:00"
            end_datetime = f"{date} {end_time}:00"

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                INSERT INTO bookings (user_id, room_id, start_time, end_time, status, token, token_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                4,
                room_id,
                start_datetime,
                end_datetime,
                "confirmed",
                token,
                False
            ))

            con.commit()
            booking_id = cur.lastrowid
            con.close()

            return {
                "status": "success",
                "message": "Room booked successfully",
                "booking_id": booking_id,
                "token": token
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    if action == "cancel_booking":
        try:
            booking_id = request.get("booking_id")

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                UPDATE bookings
                SET status = 'cancelled'
                WHERE booking_id = %s
            """, (booking_id,))

            con.commit()

            if cur.rowcount > 0:
                response = {
                    "status": "success",
                    "message": f"Booking {booking_id} cancelled successfully"
                }
            else:
                response = {
                    "status": "error",
                    "message": "Booking ID not found"
                }

            con.close()
            return response

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


    if action == "use_room":
        try:
            booking_id = request.get("booking_id")
            room_id = request.get("room_id")

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                UPDATE bookings
                SET status = 'in_use',
                    token_used = TRUE
                WHERE booking_id = %s
                AND room_id = %s
                AND status = 'confirmed'
                AND token_used = FALSE
            """, (booking_id, room_id))

            con.commit()

            if cur.rowcount > 0:
                response = {
                    "status": "success",
                    "message": f"Room {room_id} is now in use"
                }
            else:
                response = {
                    "status": "error",
                    "message": "Booking cannot be used. It may be cancelled, completed, already in use, or invalid."
                }

            con.close()
            return response

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


    if action == "return_room":
        try:
            booking_id = request.get("booking_id")
            room_id = request.get("room_id")

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                UPDATE bookings
                SET status = 'completed'
                WHERE booking_id = %s
                AND room_id = %s
                AND status = 'in_use'
            """, (booking_id, room_id))

            con.commit()

            if cur.rowcount > 0:
                response = {
                    "status": "success",
                    "message": f"Room {room_id} has been returned"
                }
            else:
                response = {
                    "status": "error",
                    "message": "Room cannot be returned. Booking is not currently in use or invalid."
                }

            con.close()
            return response

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
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