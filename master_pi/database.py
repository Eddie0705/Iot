import MySQLdb
from db_setup import get_connection
import secrets

def login_user(email, password):
    con = None

    try:
        con = get_connection()

        
        cur = con.cursor()

        cur.execute("""
            SELECT user_id, email, full_name, role
            FROM users
            WHERE email = %s
            AND password = %s
            AND status = 'active'
        """, (email, password))

        user = cur.fetchone()

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

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()

def get_booking_logs():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT b.booking_id, u.email, r.room_name, b.start_time, b.end_time, b.status, b.created_at
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN rooms r ON b.room_id = r.room_id
        ORDER BY b.created_at DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def get_usage_logs():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT l.log_id, u.email, l.action, l.details, l.created_at
        FROM system_logs l
        LEFT JOIN users u ON l.user_id = u.user_id
        ORDER BY l.created_at DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def get_booking_history(user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT b.booking_id, r.room_name, b.start_time, b.end_time, b.status
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    con.close()
    return rows

def get_all_room_status():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT room_id, room_name, location, capacity, status
        FROM rooms
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def update_room_status(room_name, status):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE rooms
        SET status = %s
        WHERE room_name = %s
    """, (status, room_name))
    con.commit()
    con.close()


def get_all_users():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT user_id, email, full_name, rmit_id, role, status FROM users")
    rows = cur.fetchall()
    con.close()
    return rows


def get_fault_reports():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT f.report_id, r.room_name, u.email, f.description, f.status, f.admin_decision, f.created_at
        FROM fault_reports f
        JOIN rooms r ON f.room_id = r.room_id
        JOIN users u ON f.reported_by = u.user_id
        ORDER BY f.created_at DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def get_fault_report_room(report_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT r.room_name
        FROM fault_reports f
        JOIN rooms r ON f.room_id = r.room_id
        WHERE f.report_id = %s
    """, (report_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None


def resolve_fault_report(report_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE fault_reports
        SET status = 'resolved'
        WHERE report_id = %s
    """, (report_id,))
    con.commit()
    con.close()


def create_security_staff(email, password, full_name, rmit_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO users (email, password, full_name, rmit_id, role)
        VALUES (%s, %s, %s, %s, 'security')
    """, (email, password, full_name, rmit_id))
    con.commit()
    con.close()


def update_user(user_id, email, full_name, role, status):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE users
        SET email = %s, full_name = %s, role = %s, status = %s
        WHERE user_id = %s
    """, (email, full_name, role, status, user_id))
    con.commit()
    con.close()


def delete_user(user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    con.commit()
    con.close()


def get_user_by_id(user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT user_id, email, full_name, rmit_id, role, status
        FROM users WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    con.close()
    return row
def log_action(user_id, action, details):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO system_logs (user_id, action, details)
            VALUES (%s, %s, %s)
        """, (user_id, action, details))

        con.commit()

    except MySQLdb.Error as e:
        print(f"Logging error: {e}")

    finally:
        if con:
            con.close()


def register_user(email, password, full_name, rmit_id=None):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        # app.py does not send rmit_id, so generate one for now
        if rmit_id is None or rmit_id == "":
            rmit_id = "TEMP-" + secrets.token_hex(4)

        cur.execute("""
            INSERT INTO users (email, password, full_name, rmit_id, role)
            VALUES (%s, %s, %s, %s, 'user')
        """, (email, password, full_name, rmit_id))

        con.commit()
        user_id = cur.lastrowid

        log_action(user_id, "REGISTER", f"New user registered: {email}")

        return {
            "status": "success",
            "message": "Registration successful",
            "user_id": user_id
        }

    except MySQLdb.IntegrityError:
        return {
            "status": "error",
            "message": "Email or RMIT ID already exists"
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def search_room(start_time, end_time):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT room_id, room_name, location, capacity, status
            FROM rooms
            WHERE status = 'available'
            AND room_id NOT IN (
                SELECT room_id
                FROM bookings
                WHERE status IN ('Booked', 'Checked In')
                AND %s < end_time
                AND %s > start_time
            )
        """, (start_time, end_time))

        rows = cur.fetchall()

        rooms = []

        for row in rows:
            rooms.append({
                "room_id": row[0],
                "room_name": row[1],
                "location": row[2],
                "capacity": row[3],
                "status": row[4]
            })

        return {
            "status": "success",
            "message": "Available rooms retrieved",
            "rooms": rooms
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def book_room(room_id, start_time, end_time, user_id=1):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT status
            FROM rooms
            WHERE room_id = %s
        """, (room_id,))

        room = cur.fetchone()

        if not room:
            return {
                "status": "error",
                "message": "Room not found"
            }

        if room[0].lower() != "available":
            return {
                "status": "error",
                "message": f"Room is currently {room[0]}"
            }

        cur.execute("""
            SELECT booking_id
            FROM bookings
            WHERE room_id = %s
            AND status IN ('Booked', 'Checked In')
            AND %s < end_time
            AND %s > start_time
        """, (room_id, start_time, end_time))

        existing_booking = cur.fetchone()

        if existing_booking:
            return {
                "status": "error",
                "message": "Room is already booked during this time"
            }

        token = secrets.token_hex(4)

        cur.execute("""
            INSERT INTO bookings (user_id, room_id, start_time, end_time, status, token, token_used)
            VALUES (%s, %s, %s, %s, 'Booked', %s, FALSE)
        """, (user_id, room_id, start_time, end_time, token))

        con.commit()
        booking_id = cur.lastrowid

        log_action(user_id, "BOOK_ROOM", f"Booking {booking_id} created for room {room_id}")

        return {
            "status": "success",
            "message": "Room booked successfully",
            "booking_id": booking_id,
            "token": token
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def cancel_booking(booking_id, user_id=1):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = %s
            AND status = 'Booked'
        """, (booking_id,))

        booking = cur.fetchone()

        if not booking:
            return {
                "status": "error",
                "message": "Booking not found or cannot be cancelled"
            }

        cur.execute("""
            UPDATE bookings
            SET status = 'Cancelled'
            WHERE booking_id = %s
        """, (booking_id,))

        con.commit()

        log_action(user_id, "CANCEL_BOOKING", f"Booking {booking_id} cancelled")

        return {
            "status": "success",
            "message": "Booking cancelled successfully"
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def use_room(booking_id, room_id, token, user_id=1):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT booking_id, room_id
            FROM bookings
            WHERE booking_id = %s
            AND room_id = %s
            AND token = %s
            AND status = 'Booked'
            AND token_used = FALSE
        """, (booking_id, room_id, token))

        booking = cur.fetchone()

        if not booking:
            return {
                "status": "error",
                "message": "Invalid token, booking not found, or token already used"
            }

        cur.execute("""
            UPDATE bookings
            SET status = 'Checked In',
                token_used = TRUE
            WHERE booking_id = %s
        """, (booking_id,))

        cur.execute("""
            UPDATE rooms
            SET status = 'In Use'
            WHERE room_id = %s
        """, (room_id,))

        con.commit()

        log_action(user_id, "USE_ROOM", f"User checked in to room {room_id}")

        return {
            "status": "success",
            "message": "Room check-in successful",
            "booking_id": booking_id,
            "room_id": room_id
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def return_room(booking_id, room_id, user_id=1):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = %s
            AND room_id = %s
            AND status = 'Checked In'
        """, (booking_id, room_id))

        booking = cur.fetchone()

        if not booking:
            return {
                "status": "error",
                "message": "No active checked-in booking found for this room"
            }

        cur.execute("""
            UPDATE bookings
            SET status = 'completed'
            WHERE booking_id = %s
        """, (booking_id,))

        cur.execute("""
            UPDATE rooms
            SET status = 'available'
            WHERE room_id = %s
        """, (room_id,))

        con.commit()

        log_action(user_id, "RETURN_ROOM", f"User returned room {room_id}")

        return {
            "status": "success",
            "message": "Room returned successfully",
            "booking_id": booking_id,
            "room_id": room_id
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()

def update_room_status(room_id, status):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            UPDATE rooms
            SET status = %s
            WHERE room_id = %s
        """, (status, room_id))

        con.commit()

        return {
            "status": "success",
            "message": f"Room {room_id} status updated to {status}"
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close() 

def get_room_status(room_id):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT room_id, room_name, location, capacity, status
            FROM rooms
            WHERE room_id = %s
        """, (room_id,))

        row = cur.fetchone()

        if not row:
            return {
                "status": "error",
                "message": "Room not found"
            }

        return {
            "status": "success",
            "room": {
                "room_id": row[0],
                "room_name": row[1],
                "location": row[2],
                "capacity": row[3],
                "room_status": row[4]
            }
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()


def get_next_booking(room_id):
    con = None

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT booking_id, start_time, end_time, status
            FROM bookings
            WHERE room_id = %s
            AND start_time >= NOW()
            AND status IN ('Booked', 'Checked In')
            ORDER BY start_time ASC
            LIMIT 1
        """, (room_id,))

        row = cur.fetchone()

        if not row:
            return {
                "status": "success",
                "message": "No upcoming booking",
                "next_booking": None
            }

        return {
            "status": "success",
            "message": "Next booking retrieved",
            "next_booking": {
                "booking_id": row[0],
                "start_time": str(row[1]),
                "end_time": str(row[2]),
                "booking_status": row[3]
            }
        }

    except MySQLdb.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {e}"
        }

    finally:
        if con:
            con.close()