import MySQLdb
from db_setup import get_connection

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
                "success": True,
                "message": "Login successful",
                "user_id": user[0],
                "email": user[1],
                "full_name": user[2],
                "role": user[3]
            }

        return {
            "success": False,
            "message": "Invalid email or password"
        }
        

    except MySQLdb.Error as e:
        return {
            "success": False,
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