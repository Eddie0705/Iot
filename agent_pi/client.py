import socket
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import MASTER_HOST, MASTER_PORT


def send_request(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((MASTER_HOST, MASTER_PORT))
            client.sendall(json.dumps(message).encode("utf-8"))

            response = client.recv(4096).decode("utf-8")
            return json.loads(response)

    except ConnectionRefusedError:
        return {
            "status": "error",
            "message": "Cannot connect to Master Pi. Is the server running?"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    test_message = {
        "action": "ping",
        "sender": "Agent Pi",
        "message": "Hello from Agent Pi"
    }

    print(send_request(test_message))