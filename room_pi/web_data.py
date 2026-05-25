import sense_emu as SenseHat
from mqtt_client import *

#commented out because sense-emu is kinda broken rn though no reason it wouldnt work on a real pi remember to change import
def getWeatherStats() -> tuple[float, float, float]:
    s = SenseHat()

    try:
        humidity = s.get_humidity()
        pressure = s.get_pressure()
        temperature = s.get_temperature()
    except Exception as e:
        print("SenseHat Weather Stats threw an Error")
        print(e)

    return (humidity, pressure, temperature)

def isBooked() -> bool:    
    RESPONSE = "response/bookings"
    if RESPONSE not in subscribeTopics:
        subscribeTopics.append(RESPONSE)
    
    with "request/bookings" as REQUEST:
        client.publish(REQUEST, "INSERT REQUEST STRING HERE")

    # Publish Request
    time.sleep(2) # Wait for response
    
    if (response[RESPONSE][-1].lower() == "false"):
        return False
    elif (response[RESPONSE][-1].lower() == "true"):
        return True
    else:
        raise TypeError(f"This topic does not return a valid result, {RESPONSE=}, {response[RESPONSE][-1].lower()=}")


def getSchedule() -> list[list[str]]:
    RESPONSE = "response/schedule"
    if RESPONSE not in subscribeTopics:
        subscribeTopics.append(RESPONSE)

    with "request/schedule" as REQUEST:
        client.publish(REQUEST, "INSERT REQUEST STRING HERE")

    time.sleep(2)
    response[RESPONSE] # response result
    
    return None