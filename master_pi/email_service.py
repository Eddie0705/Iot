import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config import EMAIL_SENDER, EMAIL_PASSWORD


def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Email failed: {e}")


def send_booking_confirmation(to_email, room_name, start_time, end_time, token):
    subject = "Room Booking Confirmed"
    body = (
        f"Your booking has been confirmed.\n\n"
        f"Room:       {room_name}\n"
        f"Start time: {start_time}\n"
        f"End time:   {end_time}\n"
        f"Token:      {token}\n\n"
        f"Use this token to check in at the room. It can only be used once.\n\n"
        f"Smart Classroom Management System"
    )
    send_email(to_email, subject, body)


def send_booking_cancellation(to_email, room_name, start_time, end_time):
    subject = "Room Booking Cancelled"
    body = (
        f"Your booking has been cancelled.\n\n"
        f"Room:       {room_name}\n"
        f"Start time: {start_time}\n"
        f"End time:   {end_time}\n\n"
        f"Smart Classroom Management System"
    )
    send_email(to_email, subject, body)
