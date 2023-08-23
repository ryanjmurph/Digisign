# Pius Gumo
# 14/08/2023
# Mysql Connection

import sys
import pymysql.cursors
from dotenv import dotenv_values

config = dotenv_values(".env")  # read the database credentials from .env file


class MYSQL:
    connection = None

    def __init__(self) -> None:
        self.connect()

    def connect(self):
        try:
            connection = pymysql.connect(
                host="localhost",
                user=config["MYSQL_USER"],
                password=config["MYSQL_PASSWORD"],
                db=config["MYSQL_DATABASE"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        except Exception as e:
            print("ERROR: Unexpected error: Could not connect to MySql instance.")
            print(e)
            sys.exit()

        print("SUCCESS: Connection to database successful.")
        self.connection = connection

    def close(self):
        self.connection.close()
        print("INFO: Database connection closed.")

    def get_connection(self):
        if self.connection == None:
            self.connect()

        return self.connection