# Smart Classroom Management System

## Project Overview

A distributed IoT classroom management system developed for COSC2674/2755 Programming Internet of Things (Semester 1, 2026).

The system manages university classroom bookings, room monitoring, and admin control across multiple Raspberry Pi devices. Communication is handled via MQTT (publish-subscribe) and Socket Programming (request-response), with data persisted in a centralized remote MySQL database.

---

## Team Members & Division of Work

| Name                 | Student ID | Responsibilities                                                                                           |
| -------------------- | ---------- | ---------------------------------------------------------------------------------------------------------- |
| Halbert Lie Setiawan | S3962208   | Master Pi — socket server, database design, booking logic                                                  |
| Henry Pham           | S4053540   | Agent Pi — user registration, login, room booking interface                                                |
| Abdul Wajid Khan     | S4172021   | Room Pi — room display, environmental monitoring, Sense HAT                                                |
| Yong Tian Goh        | S4025884   | Admin — admin dashboard, user management, reports, unit testing, enhancement, readme, desgin pattern, mqtt |

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
- Displays room status (colour-coded), today's booking schedule, and live environmental readings (temperature, humidity, pressure) from Sense HAT
- Users check in by entering their booking token — validated against Master Pi via socket
- Automatically checks out bookings when the end time is reached
- Communicates with Master Pi via socket programming

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
- Book a room — receive a one-time token and QR code on success
- Cancel a booking
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

### Room Pi

- Displays room name, colour-coded status (green=available, blue=in use, yellow=maintenance, red=fault)
- Shows today's booking schedule with user names and times
- Live weather readings (temperature, humidity, pressure) from Sense HAT, auto-refreshed every 10 seconds
- Token check-in form — user enters their booking token to check in, room status updates to In Use
- Automatic checkout when booking end time is reached (background thread checks every 60 seconds)

### Security Staff (Agent Pi)

- Login via Agent Pi
- Change room status (e.g. In Use → Maintenance)
- Receive visual Sense HAT alert when a room enters Fault status

---

## Custom Enhancements

### Enhancement 1 — Email Notifications

Automated emails are sent to users on key booking events using Python's `smtplib` with Gmail SMTP:

- **Booking confirmation** — sent immediately after a room is successfully booked, includes the room name, time slot, and one-time access token
- **Booking cancellation** — sent when a booking is cancelled, includes the room and time details

Emails are generated and dispatched server-side in `master_pi/email_service.py`, triggered from within `database.py` after each booking or cancellation is committed to the database. This removes the need for users to manually note down their token — it is delivered directly to their inbox.

### Enhancement 2 — QR Code Booking Token

When a booking is confirmed, a QR code is automatically generated from the booking ID and access token using the `qrcode` Python library. The QR code is displayed on the Agent Pi booking confirmation page.

The QR code encodes `{"booking_id": X, "token": "XXXX"}` as JSON, allowing the Room Pi to read both values from a single scan using a camera module. This replaces manual token entry at the Room Pi with a faster, more user-friendly scan-based check-in — similar to how boarding passes or cinema tickets work in practice.

The generation logic lives in `agent_pi/qr_service.py` and is rendered inline as a base64 image, requiring no file storage or additional endpoints.

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd group-assignment-group-37
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

> **Note:** `--system-site-packages` is required on Raspberry Pi so the venv can access the system-installed `sense-hat` package (installed via `apt-get`). Without it, the Sense HAT import will fail with a missing `RTIMU` module error.

### 3. Install dependencies

Dependencies differ per device:

**Master Pi / Admin Pi:**

```bash
pip install flask paho-mqtt pymysql matplotlib pytest qrcode[pil]
```

**Agent Pi:**

```bash
pip install flask paho-mqtt pymysql qrcode[pil]
```

**Room Pi (emulator — PC/laptop):**

```bash
pip install flask paho-mqtt sense-emu
```

**Room Pi (real Raspberry Pi):**

```bash
pip install flask paho-mqtt
sudo apt-get install sense-hat
```

> **Note:** Do **not** install `sense-hat` via pip on a real Pi — install it via apt instead. The native `RTIMU` module is only available through the system apt package. Also ensure the venv is created with `--system-site-packages` so it can access the apt-installed version.

### 4. Set up the database (run once)

```bash
cd master_pi
python3 db_init.py
python3 db_seed.py
```

### 5. Start MQTT broker on Master Pi

```bash
sudo systemctl start mosquitto
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

### 9. Run the room display app (Room Pi)

Set `ROOM_ID` to the database ID of the room this Pi physically represents:

```bash
cd room_pi
ROOM_ID=1 python3 app.py
```

The room display will be available at `http://localhost:5003`. It shows the room's current status (colour-coded), today's booking schedule, and live environmental readings from the Sense HAT.

---

## Running Unit Tests

```bash
python3 -m pytest tests/ -v
```

Tests cover (36 tests total):

- Authentication — login success/failure, registration, duplicate email, DB errors
- Booking — book room, token uniqueness, time conflicts, room not found, maintenance/fault blocking
- Room state transitions — valid/invalid status updates, connection cleanup
- MQTT — announcement and room status published to correct topics
- Error handling — DB errors, wrong credentials, empty results

---

## Command to open MySQL in the terminal (only Master Pi has access)

```
mysql -h 34.30.131.18 -u root -p")VZ3FKr&B&nH" room_booking
```

## Challenges Encountered

- **MySQL installation on macOS** — `mysqlclient` failed to compile due to missing `zstd` library. Resolved by using `PyMySQL` with `install_as_MySQLdb()` as a drop-in replacement.
- **Google Cloud SQL firewall** — University (RMIT) network blocks port 3306. Development required switching to a mobile hotspot or whitelisting the IP in Google Cloud Console.
- **Module imports across directories** — Python's relative imports don't work when running Flask apps as scripts. Resolved using `sys.path.insert()` to add sibling directories to the import path.
- **MQTT broker configuration** — Initial setup used `localhost` as broker address. Updated to use the Master Pi's IP so all devices on the network can publish and subscribe.
- **MQTT publish reliability** — Using `client.publish()` followed by immediate `disconnect()` dropped messages before they were delivered. Replaced with `mqtt_publish.single()` which waits for delivery confirmation before returning.
- **Duplicate function shadowing** — Python silently uses the last definition when two functions share the same name. A duplicate `update_room_status` at the bottom of `database.py` was overriding the version with MQTT publish, causing status updates to succeed in the database but never notify subscribers.
- **Sense HAT in virtual environment** — Installing `sense-hat` via pip fails at runtime because the native `RTIMU` module is only available through the system apt package. The fix is to create the venv with `--system-site-packages` so it can access the apt-installed version.
- **Room status case mismatch** — Seed data stored room status as `'Available'` (capital A) but booking logic compared against `'available'` (lowercase), blocking all bookings. Fixed by normalising the check to only block `maintenance` and `fault` statuses, case-insensitively.
- **Socket blocking on unreachable host** — Room Pi hung indefinitely when the Master Pi IP was unreachable. Fixed by setting a 3-second socket timeout so the page loads with fallback values instead of hanging.

---

## Lessons Learned

- Designing the database schema upfront saves significant refactoring time — adding the `fault_reports` table later required updating the drop order in `db_init.py` due to foreign key constraints.
- Mocking is essential for unit testing database and MQTT code — tests should not depend on real connections to be reliable and fast.
- Separating database query functions into `database.py` from Flask routes keeps code modular and makes testing significantly easier.
- MQTT and socket serve different purposes — MQTT is best for broadcast/one-to-many, sockets for direct request-response between two devices.
