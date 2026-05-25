import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'admin_pi'))

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

from master_pi.database import update_room_status, get_all_room_status, get_fault_reports


class TestMQTT(unittest.TestCase):

    @patch("paho.mqtt.client.Client")
    def test_announcement_published_to_correct_topic(self, mock_mqtt_class):
        mock_client = MagicMock()
        mock_mqtt_class.return_value = mock_client

        from admin_pi.mqtt_admin import publish_announcement
        publish_announcement("Room A204 down, waiting for maintenance")

        mock_client.publish.assert_called_once_with(
            "admin/announcements",
            "Room A204 down, waiting for maintenance"
        )

    @patch("paho.mqtt.client.Client")
    def test_room_status_published_to_correct_topic(self, mock_mqtt_class):
        mock_client = MagicMock()
        mock_mqtt_class.return_value = mock_client

        from admin_pi.mqtt_admin import publish_room_status
        publish_room_status("A204", "fault")

        mock_client.publish.assert_called_once_with(
            "rooms/A204/status",
            "fault"
        )

    @patch("paho.mqtt.client.Client")
    def test_mqtt_connects_before_publishing(self, mock_mqtt_class):
        mock_client = MagicMock()
        mock_mqtt_class.return_value = mock_client

        from admin_pi.mqtt_admin import publish_announcement
        publish_announcement("test")

        mock_client.connect.assert_called_once()
        mock_client.publish.assert_called_once()
        mock_client.disconnect.assert_called_once()


class TestRoomStateTransitions(unittest.TestCase):

    VALID_STATUSES = ["available", "in_use", "maintenance", "fault"]

    @patch("master_pi.database.get_connection")
    def test_update_to_valid_status(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur

        for status in self.VALID_STATUSES:
            update_room_status("A101", status)
            mock_cur.execute.assert_called_with(
                """
        UPDATE rooms
        SET status = %s
        WHERE room_name = %s
    """,
                (status, "A101")
            )

    @patch("master_pi.database.get_connection")
    def test_update_room_commits(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur

        update_room_status("A101", "fault")

        mock_con.commit.assert_called_once()

    @patch("master_pi.database.get_connection")
    def test_update_room_closes_connection(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur

        update_room_status("A101", "maintenance")

        mock_con.close.assert_called_once()

    @patch("master_pi.database.get_connection")
    def test_get_all_room_status_returns_rows(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = [
            (1, "A204", "Building A", 30, "available"),
            (2, "B301", "Building B", 50, "fault")
        ]

        rows = get_all_room_status()

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], "A204")
        self.assertEqual(rows[1][4], "fault")


class TestErrorHandling(unittest.TestCase):

    @patch("master_pi.database.get_connection")
    def test_login_db_error_returns_error_response(self, mock_get_connection):
        import MySQLdb
        mock_get_connection.side_effect = MySQLdb.Error("DB connection failed")

        from master_pi.database import login_user
        result = login_user("test@test.com", "password")

        self.assertFalse(result["success"])
        self.assertIn("Database error", result["message"])

    @patch("master_pi.database.get_connection")
    def test_login_wrong_credentials_returns_failure(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        from master_pi.database import login_user
        result = login_user("wrong@test.com", "wrongpassword")

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid email or password")

    @patch("master_pi.database.get_connection")
    def test_get_fault_reports_handles_empty(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = []

        rows = get_fault_reports()

        self.assertEqual(rows, [])

    @patch("master_pi.database.get_connection")
    def test_connection_always_closed_on_error(self, mock_get_connection):
        import MySQLdb
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.execute.side_effect = MySQLdb.Error("Query failed")

        from master_pi.database import login_user
        login_user("test@test.com", "password")

        mock_con.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
