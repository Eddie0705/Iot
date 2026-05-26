from sense_emu import SenseHat
from mqtt_client import *

#commented out because sense-emu is kinda broken rn though no reason it wouldnt work on a real pi remember to change import
def getWeatherStats() -> tuple[float, float, float]:
    s = SenseHat()
    humidity, pressure, temperature = -1,-1,-1

    try:
        humidity = s.get_humidity()
        pressure = s.get_pressure()
        temperature = s.get_temperature()
    except Exception as e:
        print("SenseHat Weather Stats threw an Error")
        print(e)

    return (humidity, pressure, temperature)

def getStatus():
    with "room/request/status" as REQUEST:
        client.publish(REQUEST, json.dumps({
            "action": "get_room_status",
            "id": ROOMID
        }).encode())

    time.sleep(2) # Wait for response

    return response["get_room_status"]["status"]

def getSchedule():
    with "room/request/schedule" as REQUEST:
        client.publish(REQUEST, json.dumps({
            "action": "get_room_schedule",
            "id": ROOMID
        }).encode())

    time.sleep(2) # Wait for response

    return response["get_room_schedule"]["schedule"]