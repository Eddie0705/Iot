import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


def get_connection():
    return MySQLdb.connect(
        host="34.30.131.18",
        user="root",
        passwd=")VZ3FKr&B&nH",
        db="room_booking"
    )