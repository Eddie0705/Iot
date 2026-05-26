import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master_pi'))

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

from master_pi.database import login_user, register_user


class TestLogin(unittest.TestCase):

    @patch("master_pi.database.get_connection")
    def test_login_success(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (1, "alice@rmit.edu.au", "Alice Smith", "user")

        result = login_user("alice@rmit.edu.au", "pass123")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["email"], "alice@rmit.edu.au")
        self.assertEqual(result["role"], "user")

    @patch("master_pi.database.get_connection")
    def test_login_wrong_password(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        result = login_user("alice@rmit.edu.au", "wrongpassword")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Invalid email or password")

    @patch("master_pi.database.get_connection")
    def test_login_nonexistent_user(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        result = login_user("nobody@rmit.edu.au", "pass123")

        self.assertEqual(result["status"], "error")

    @patch("master_pi.database.get_connection")
    def test_login_db_error(self, mock_get_connection):
        mock_get_connection.side_effect = MySQLdb.Error("Connection failed")

        result = login_user("alice@rmit.edu.au", "pass123")

        self.assertEqual(result["status"], "error")
        self.assertIn("Database error", result["message"])

    @patch("master_pi.database.get_connection")
    def test_login_returns_user_id(self, mock_get_connection):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (4, "alice@rmit.edu.au", "Alice Smith", "user")

        result = login_user("alice@rmit.edu.au", "pass123")

        self.assertEqual(result["user_id"], 4)


class TestRegistration(unittest.TestCase):

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_register_success(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.lastrowid = 5

        result = register_user("bob@rmit.edu.au", "pass123", "Bob Jones", "S3001099")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["user_id"], 5)

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_register_duplicate_email(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.execute.side_effect = MySQLdb.IntegrityError("Duplicate entry")

        result = register_user("alice@rmit.edu.au", "pass123", "Alice Smith", "S3001001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Email or RMIT ID already exists")

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_register_generates_rmit_id_if_missing(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.lastrowid = 6

        result = register_user("new@rmit.edu.au", "pass123", "New User", rmit_id=None)

        args = mock_cur.execute.call_args[0]
        inserted_rmit_id = args[1][3]
        self.assertTrue(inserted_rmit_id.startswith("TEMP-"))

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_register_logs_action(self, mock_get_connection, mock_log):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_get_connection.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.lastrowid = 7

        register_user("carol@rmit.edu.au", "pass123", "Carol White", "S3001010")

        mock_log.assert_called_once()

    @patch("master_pi.database.log_action")
    @patch("master_pi.database.get_connection")
    def test_register_db_error(self, mock_get_connection, mock_log):
        mock_get_connection.side_effect = MySQLdb.Error("DB error")

        result = register_user("error@rmit.edu.au", "pass123", "Error User", "S9999999")

        self.assertEqual(result["status"], "error")
        self.assertIn("Database error", result["message"])


if __name__ == "__main__":
    unittest.main()
