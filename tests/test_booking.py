import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

from master_pi.database import book_room, cancel_booking, use_room


class TestBookRoom(unittest.TestCase):

    @patch("master_pi.database.send_booking_confirmation")
    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_book_room_success_returns_token(self, mock_get_connection, mock_log, mock_email):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.side_effect = [
            ("available",),           # room status check
            None,                     # no existing booking conflict
            ("alice@rmit.edu.au",),   # user email for confirmation
            ("A204",)                 # room name for confirmation
        ]
        mock_cur.lastrowid = 1

        result = book_room(1, "2026-05-25 09:00:00", "2026-05-25 11:00:00", user_id=4)

        self.assertEqual(result["status"], "success")
        self.assertIn("token", result)
        self.assertIsNotNone(result["token"])

    @patch("master_pi.database.send_booking_confirmation")
    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_book_room_token_is_unique(self, mock_get_connection, mock_log, mock_email):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.side_effect = [
            ("available",), None, ("alice@rmit.edu.au",), ("A204",),
            ("available",), None, ("bob@rmit.edu.au",), ("A204",)
        ]
        mock_cur.lastrowid = 1

        result1 = book_room(1, "2026-05-25 09:00:00", "2026-05-25 11:00:00", user_id=4)
        result2 = book_room(1, "2026-05-25 12:00:00", "2026-05-25 14:00:00", user_id=5)

        self.assertNotEqual(result1["token"], result2["token"])

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_book_room_not_found(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        result = book_room(999, "2026-05-25 09:00:00", "2026-05-25 11:00:00", user_id=4)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Room not found")

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_book_room_already_occupied(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ("maintenance",)

        result = book_room(1, "2026-05-25 09:00:00", "2026-05-25 11:00:00", user_id=4)

        self.assertEqual(result["status"], "error")
        self.assertIn("maintenance", result["message"])

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_book_room_time_conflict(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.side_effect = [
            ("available",),  # room is available
            (1,)             # but existing booking conflicts
        ]

        result = book_room(1, "2026-05-25 09:00:00", "2026-05-25 11:00:00", user_id=4)

        self.assertEqual(result["status"], "error")
        self.assertIn("already booked", result["message"])


class TestCancelBooking(unittest.TestCase):

    @patch("master_pi.database.send_booking_cancellation")
    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_cancel_booking_success(self, mock_get_connection, mock_log, mock_email):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (
            1, "alice@rmit.edu.au", "A204",
            "2026-05-25 09:00:00", "2026-05-25 11:00:00"
        )

        result = cancel_booking(1, user_id=4)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Booking cancelled successfully")

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_cancel_booking_not_found(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        result = cancel_booking(999, user_id=4)

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])


class TestUseRoom(unittest.TestCase):

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_use_room_success(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (1, 1)

        result = use_room(1, 1, "TOKEN-ABC123", user_id=4)

        self.assertEqual(result["status"], "success")

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_use_room_invalid_token(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        result = use_room(1, 1, "WRONG-TOKEN", user_id=4)

        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid token", result["message"])

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_use_room_token_marked_as_used(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (1, 1)

        use_room(1, 1, "TOKEN-ABC123", user_id=4)

        calls = [str(c) for c in mock_cur.execute.call_args_list]
        self.assertTrue(any("token_used = TRUE" in c for c in calls))


if __name__ == "__main__":
    unittest.main()
