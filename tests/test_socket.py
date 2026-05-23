import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent_pi'))

from agent_pi.client import send_request


class TestSocketMessageFormat(unittest.TestCase):

    @patch("agent_pi.client.socket.socket")
    def test_message_sent_as_valid_json(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = json.dumps({"status": "success"}).encode("utf-8")

        send_request({"action": "ping"})

        sent_data = mock_socket.sendall.call_args[0][0]
        parsed = json.loads(sent_data.decode("utf-8"))
        self.assertIsInstance(parsed, dict)

    @patch("agent_pi.client.socket.socket")
    def test_message_contains_action_field(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = json.dumps({"status": "success"}).encode("utf-8")

        send_request({"action": "login", "email": "test@rmit.edu.au", "password": "pass"})

        sent_data = mock_socket.sendall.call_args[0][0]
        parsed = json.loads(sent_data.decode("utf-8"))
        self.assertIn("action", parsed)
        self.assertEqual(parsed["action"], "login")

    @patch("agent_pi.client.socket.socket")
    def test_response_is_parsed_from_json(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = json.dumps({
            "status": "success",
            "message": "Login successful"
        }).encode("utf-8")

        result = send_request({"action": "login"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Login successful")

    @patch("agent_pi.client.socket.socket")
    def test_connection_refused_returns_error(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = ConnectionRefusedError

        result = send_request({"action": "ping"})

        self.assertEqual(result["status"], "error")
        self.assertIn("Cannot connect to Master Pi", result["message"])

    @patch("agent_pi.client.socket.socket")
    def test_unexpected_error_returns_error(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = Exception("Network failure")

        result = send_request({"action": "ping"})

        self.assertEqual(result["status"], "error")
        self.assertIn("Network failure", result["message"])


if __name__ == "__main__":
    unittest.main()
