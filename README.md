# Smart Classroom Management System

## Project Overview

A distributed IoT classroom management system developed for COSC2674/2755 Programming Internet of Things (Semester 1, 2026).

The system manages university classroom bookings, room monitoring, and admin control across multiple Raspberry Pi devices. Communication is handled via MQTT (publish-subscribe) and Socket Programming (request-response), with data persisted in a centralized remote MySQL database.

---

## Team Members & Division of Work

| Name | Student ID | Responsibilities |
|------|------------|-----------------|
| Member 1 | S3XXXXXX | Master Pi — socket server, database design, booking logic |
| Member 2 | S3XXXXXX | Agent Pi — user registration, login, room booking interface |
| Member 3 | S3XXXXXX | Room Pi — room display, environmental monitoring, Sense HAT |
| Member 4 | S3XXXXXX | Admin Pi — admin dashboard, user management, reports, unit testing |

---

## System Architecture

The system consists of four components:

**Master Pi**
- Central hub running on a dedicated Raspberry Pi
- Hosts the admin web interface (Flask, port 3000)
- Runs the socket server (port 5050) to handle requests from Agent Pi and Room Pi
- Connects directly to the remote MySQL database (Google Cloud SQL)
- Runs the Mosquitto MQTT broker

**Agent Pi**
- Personal device for each user/staff member
- Hosts a Flask web interface for registration, login, room search, booking, and cancellation
- Communicates with Master Pi via socket programming
- Subscribes to MQTT topics for announcements and alerts

**Room Pi**
- One per classroom
- Displays room status, upcoming bookings, and environmental readings (temperature, humidity, pressure)
- Receives room status updates via MQTT
- Uses Sense HAT for visual fault alerts

**Remote Database (Google Cloud SQL — MySQL)**
- Accessible only from Master Pi
- Tables: `users`, `rooms`, `bookings`, `system_logs`, `fault_reports`

### Communication Flow

```
Agent Pi  ──socket──►  Master Pi  ◄──socket──  Room Pi
                           │
                      [MySQL DB]
                           │
                        [MQTT Broker]
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
      Agent Pi          Room Pi          Admin Pi
   (subscriber)      (subscriber)      (publisher)
```

---

## Features

### User (Agent Pi)
- Register with email, password, full name, RMIT ID
- Login and logout
- Search available rooms by time slot
- Book a room — receive a one-time token on success
- Cancel a booking
- Check in and return a room
- Report a room fault

### Admin (Master Pi)
- Login via Master Pi web interface
- View and edit user accounts
- Create and delete security staff accounts
- View booking logs and usage logs
- View and update room status
- Review fault reports and confirm fault decisions
- Publish MQTT announcements to all devices
- Generate data visualization reports (booking frequency, booking status)

### Security Staff (Agent Pi)
- Login via Agent Pi
- Change room status (e.g. In Use → Maintenance)
- Receive visual Sense HAT alert when a room enters Fault status

---

## Custom Enhancements

### Enhancement 1 — [Name your enhancement here]
<!-- Describe your first custom enhancement, what it does, why it's novel and useful -->

### Enhancement 2 — [Name your enhancement here]
<!-- Describe your second custom enhancement, what it does, why it's novel and useful -->

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd group-assignment-group-37
```

### 2. Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install flask paho-mqtt pymysql matplotlib pytest
```

### 4. Set up the database (run once)
```bash
cd master_pi
python3 db_init.py
python3 db_seed.py
```

### 5. Start MQTT broker on Master Pi
```bash
mosquitto
```

### 6. Run the admin web app (Master Pi)
```bash
cd admin_pi
python3 app.py
```

### 7. Run the socket server (Master Pi)
```bash
cd master_pi
python3 master_server.py
```

### 8. Run the agent web app (Agent Pi)
```bash
cd agent_pi
python3 app.py
```

---

## Running Unit Tests

```bash
python3 -m pytest tests/ -v
```

Tests cover:
- MQTT message format and topic correctness
- Room state transitions
- Error and exception handling
- Authentication logic
- User input validation

---

## Challenges Encountered

- **MySQL installation on macOS** — `mysqlclient` failed to compile due to missing `zstd` library. Resolved by using `PyMySQL` with `install_as_MySQLdb()` as a drop-in replacement.
- **Google Cloud SQL firewall** — University (RMIT) network blocks port 3306. Development required switching to a mobile hotspot or whitelisting the IP in Google Cloud Console.
- **Module imports across directories** — Python's relative imports don't work when running Flask apps as scripts. Resolved using `sys.path.insert()` to add sibling directories to the import path.
- **MQTT broker configuration** — Initial setup used `localhost` as broker address. Updated to use the Master Pi's IP so all devices on the network can publish and subscribe.

---

## Lessons Learned

- Designing the database schema upfront saves significant refactoring time — adding the `fault_reports` table later required updating the drop order in `db_init.py` due to foreign key constraints.
- Mocking is essential for unit testing database and MQTT code — tests should not depend on real connections to be reliable and fast.
- Separating database query functions into `database.py` from Flask routes keeps code modular and makes testing significantly easier.
- MQTT and socket serve different purposes — MQTT is best for broadcast/one-to-many, sockets for direct request-response between two devices.
