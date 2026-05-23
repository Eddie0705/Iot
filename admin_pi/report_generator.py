import sys
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))
from db_setup import get_connection

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static")


def generate_booking_frequency_chart():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT r.room_name, COUNT(b.booking_id) as total
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        GROUP BY r.room_name
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    con.close()

    rooms = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(rooms, counts, color="steelblue")
    ax.set_title("Booking Frequency by Room")
    ax.set_xlabel("Room")
    ax.set_ylabel("Number of Bookings")
    ax.set_xticks(range(len(rooms)))
    ax.set_xticklabels(rooms, rotation=45, ha="right")
    plt.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "booking_frequency.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_booking_status_chart():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT status, COUNT(*) as total
        FROM bookings
        GROUP BY status
    """)
    rows = cur.fetchall()
    con.close()

    labels = [row[0] for row in rows]
    sizes = [row[1] for row in rows]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title("Bookings by Status")
    plt.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "booking_status.png")
    fig.savefig(path)
    plt.close(fig)
    return path
