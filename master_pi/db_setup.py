import MySQLdb
import sys


def get_connection():
    return MySQLdb.connect(
        host="34.30.131.18",
        user="root",
        passwd=")VZ3FKr&B&nH" + '#'+ "7C",
        db="room_booking"
    )


con = None

try:
    con = get_connection()

    with con:
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS system_logs")
        cur.execute("DROP TABLE IF EXISTS bookings")
        cur.execute("DROP TABLE IF EXISTS rooms")
        cur.execute("DROP TABLE IF EXISTS users")

        cur.execute("""
            CREATE TABLE users(
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                rmit_id VARCHAR(50) UNIQUE NOT NULL,
                role VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE rooms(
                room_id INT AUTO_INCREMENT PRIMARY KEY,
                room_name VARCHAR(50) UNIQUE NOT NULL,
                location VARCHAR(255) NOT NULL,
                capacity INT NOT NULL,
                status VARCHAR(50) NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE bookings(
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                room_id INT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                status VARCHAR(50) NOT NULL,
                token VARCHAR(100) UNIQUE,
                token_used BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(room_id) REFERENCES rooms(room_id)
            )
        """)

        cur.execute("""
            CREATE TABLE system_logs(
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        con.commit()
        print("Cloud MySQL tables created successfully.")

except MySQLdb.Error as e:
    print(f"MySQL error: {e}")
    sys.exit(1)

finally:
    if con:
        con.close()