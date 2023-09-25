# Pius Gumo
# 14/08/2023
# Mysql Connection

import sys
import pymysql.cursors
from dotenv import dotenv_values

config = dotenv_values(".env")  # read the database credentials from .env file


import pymysql
import sys

class MYSQL:
    """
    This class represents a MySQL database connection. It uses a singleton pattern to ensure that only one instance of the class is created.

    Attributes:
        connection (pymysql.connections.Connection): The connection object used to connect to the database.
        _instance (MYSQL): The singleton instance of the class.

    Methods:
        __init__(): Initializes the class and calls the get_connection() method.
        __new__(cls): Overrides the __new__ method to ensure that only one instance of the class is created.
        connect(): Connects to the MySQL database using the configuration parameters specified in the config file.
        close(): Closes the database connection.
        get_connection(): Returns the database connection object. If no connection exists, it creates a new one.
    """

    connection = None
    _instance = None

    def __init__(self) -> None:
        """
        Initializes the class and calls the get_connection() method.
        """
        self.get_connection()

    def __new__(cls):
        """
        Overrides the __new__ method to ensure that only one singleton instance of the class is created.
        """
        if cls._instance is None:
            print("Creating new instance")
            cls._instance = super().__new__(cls)
            cls._instance.connect()
        return cls._instance

    def connect(self):
        """
        Connects to the MySQL database using the configuration parameters specified in the config file.
        """
        try:
            connection = pymysql.connect(
                host=config["MYSQL_HOST"],
                user=config["MYSQL_USER"],
                password=config["MYSQL_PASSWORD"],
                db=config["MYSQL_DATABASE"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
        except Exception as e:
            print("ERROR: Unexpected error: Could not connect to MySql instance.")
            print(e)
            sys.exit()

        print("SUCCESS: Connection to database successful.")
        # print the class calling this method
        print(self.__class__.__name__)
        self.connection = connection

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()
        print("INFO: Database connection closed.")

    def get_connection(self):
        """
        Returns the database connection object. If no connection exists, it creates a new one.
        """
        if self.connection == None:
            print("No connection found, creating new connection")
            self.connect()

        return self.connection
