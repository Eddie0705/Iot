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
            WHERE email = ?
            AND password = ?
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