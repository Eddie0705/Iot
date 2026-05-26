import os
from socket_client import send_message

try:
    from sense_emu import SenseHat
except ImportError:
    SenseHat = None

ROOM_ID = int(os.environ.get("ROOM_ID", 1))

_sense = None
if SenseHat is not None:
    try:
        _sense = SenseHat()
    except Exception as e:
        print(f"SenseHat init error: {e}")


def getWeatherStats() -> tuple[float, float, float]:
    if _sense is None:
        return (-1, -1, -1)
    try:
        return (_sense.get_humidity(), _sense.get_pressure(), _sense.get_temperature())
    except Exception as e:
        print(f"SenseHat error: {e}")
        return (-1, -1, -1)


def getStatus() -> str:
    response = send_message({"action": "get_room_status", "room_id": ROOM_ID})
    if response.get("status") == "success":
        return response.get("room_status", "unknown")
    return "unknown"


def getRoomName() -> str:
    response = send_message({"action": "get_room_status", "room_id": ROOM_ID})
    if response.get("status") == "success":
        return response.get("room_name", f"Room {ROOM_ID}")
    return f"Room {ROOM_ID}"


def getSchedule() -> list:
    response = send_message({"action": "get_room_schedule", "room_id": ROOM_ID})
    if response.get("status") == "success":
        return response.get("bookings", [])
    return []
