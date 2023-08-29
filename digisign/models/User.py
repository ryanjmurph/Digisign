from datetime import datetime

from flask_login import UserMixin
from database.database import MYSQL

connection = MYSQL().get_connection()


class User:
    id = None
    name = None
    email = None
    password = None
    type = None
    created_at = None
    updated_at = None

    def __init__(
        self,
        id=None,
        name=None,
        email=None,
        password=None,
        type=None,
        created_at=None,
        updated_at=None,
    ) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def find(self, email):
        print(f"Trying to find user with email {email}")
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email))
            result = cursor.fetchone()
            if result:
                return self.setPropertiesOfUser(result)
            else:
                return None

    def findById(self, id):
        print(f"Trying to find user with id {id}")
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchone()
            if result:
                return self.setPropertiesOfUser(result)
            else:
                return None

    def noLines():
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(email) from USERS"
            cursor.execute(sql)
            result = cursor.fetchone()
            count = result["COUNT(email)"]
            return count

    def insert(self):
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (name, email, password, type, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)"

            cursor.execute(
                sql,
                (
                    self.name,
                    self.email,
                    self.password,
                    self.type,
                    self.created_at,
                    self.updated_at,
                ),
            )
            connection.commit()
            self.id = cursor.lastrowid
        return self

    def setPropertiesOfUser(self, user):
        self.id = user["id"]
        self.name = user["name"]
        self.email = user["email"]
        self.password = user["password"]
        self.type = user["type"]
        self.created_at = user["created_at"]
        self.updated_at = user["updated_at"]
        return self

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
