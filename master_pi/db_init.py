import sys
from db_setup import get_connection

con = None

try:
    print("Initializing database...")
    con = get_connection()
    print("Connected to database successfully.")
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

    cur.execute("""
                CREATE TABLE fault_reports(
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    reported_by INT NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    admin_decision TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(room_id) REFERENCES rooms(room_id),
    FOREIGN KEY(reported_by) REFERENCES users(user_id)
)
    """)

    con.commit()
    print("Tables created successfully.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

finally:
    if con:
        con.close()
