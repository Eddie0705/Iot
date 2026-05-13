# Smart Classroom Management System

## Project Overview

This project is an IoT-based smart classroom management system developed for COSC2674/2755 Programming Internet of Things.

The system allows:
- room booking
- classroom monitoring
- MQTT-based announcements
- room status updates
- admin and security management
- real-time communication between Raspberry Pis

The project uses Flask, MQTT, socket programming, SQLite/MySQL, and Raspberry Pi technologies.

---

## Team Members

| Name | Role |
|---|---|
| Member 1 | Master Pi |
| Member 2 | Agent Pi |
| Member 3 | Room Pi |
| Your Name | Admin, Security, Testing, Documentation |

---

## Technologies Used

- Python
- Flask
- MQTT (Mosquitto + Paho MQTT)
- Socket Programming
- SQLite / MySQL
- HTML/CSS
- Bootstrap
- Raspberry Pi
- Sense HAT

---

## Project Structure
admin_pi/
- Flask admin dashboard
- MQTT announcement publisher
- Reporting system
- Room status management

agent_pi/
- User booking interface
- Login/register system

room_pi/
- Room monitoring display
- Environmental sensor readings
- Room availability display

## Installation

### Create virtual environment

python3 -m venv venv

### Activate virtual environment

source venv/bin/activate

### Install dependencies

pip install flask
pip install paho-mqtt

### Run Flask app

python app.py

## MQTT Broker Setup

Install Mosquitto:

brew install mosquitto

Start Mosquitto:

brew services start mosquitto

## Admin Features

- Admin login
- Dashboard interface
- Send MQTT announcements
- View room logs
- Generate reports
- Update room status

