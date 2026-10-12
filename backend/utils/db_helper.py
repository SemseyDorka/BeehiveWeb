import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.environ["MYSQL_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"]
}

def connect_to_db():
    return mysql.connector.connect(**DB_CONFIG)

