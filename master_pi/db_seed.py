import sys
from db_setup import get_connection

con = None

try:
    con = get_connection()
    cur = con.cursor()

    # Users: admin, security staff, regular users
    cur.execute("""
        INSERT INTO users (email, password, full_name, rmit_id, role) VALUES
        ('admin@rmit.edu.au', 'admin123', 'Admin User', 'ADMIN001', 'admin'),
        ('security1@rmit.edu.au', 'sec123', 'John Security', 'SEC001', 'security'),
        ('security2@rmit.edu.au', 'sec123', 'Jane Security', 'SEC002', 'security'),
        ('student1@student.rmit.edu.au', 'pass123', 'Alice Smith', 'S3001001', 'user'),
        ('student2@student.rmit.edu.au', 'pass123', 'Bob Jones', 'S3001002', 'user'),
        ('teacher1@rmit.edu.au', 'pass123', 'Dr. Carol White', 'E0001001', 'user')
    """)

    # Rooms
    cur.execute("""
        INSERT INTO rooms (room_name, location, capacity, status) VALUES
        ('A204', 'Building A, Level 2', 30, 'available'),
        ('B301', 'Building B, Level 3', 50, 'available'),
        ('C105', 'Building C, Level 1', 20, 'maintenance'),
        ('D402', 'Building D, Level 4', 40, 'available')
    """)

    # Bookings
    cur.execute("""
        INSERT INTO bookings (user_id, room_id, start_time, end_time, status, token, token_used) VALUES
        (4, 1, '2026-05-18 09:00:00', '2026-05-18 11:00:00', 'Booked', 'TOKEN-ABC123', FALSE),
        (5, 2, '2026-05-18 13:00:00', '2026-05-18 15:00:00', 'Booked', 'TOKEN-DEF456', FALSE),
        (6, 1, '2026-05-19 10:00:00', '2026-05-19 12:00:00', 'Booked', 'TOKEN-GHI789', FALSE),
        (4, 4, '2026-05-17 09:00:00', '2026-05-17 11:00:00', 'completed', 'TOKEN-JKL012', TRUE)
    """)

    # System logs
    cur.execute("""
        INSERT INTO system_logs (user_id, action, details) VALUES
        (4, 'login', 'User logged in'),
        (4, 'booking_created', 'Booked room A204 for 2026-05-18 09:00'),
        (5, 'login', 'User logged in'),
        (5, 'booking_created', 'Booked room B301 for 2026-05-18 13:00'),
        (1, 'login', 'Admin logged in'),
        (1, 'room_status_updated', 'Updated C105 status to maintenance')
    """)

    # Fault reports
    cur.execute("""
        INSERT INTO fault_reports (room_id, reported_by, description, status) VALUES
        (3, 4, 'Projector not working and AC broken', 'pending'),
        (1, 5, 'Lights flickering', 'pending')
    """)

    con.commit()
    print("Sample data inserted successfully.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

finally:
    if con:
        con.close()
