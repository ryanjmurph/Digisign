from datetime import datetime
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

        # log the details of the post
        print(
            f"Name: {self.name}, Email: {self.email}, Password: {self.password}, Type: {self.type}, Created At: {self.created_at}, Updated At: {self.updated_at}"
        )

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def find(self, email):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email))
            result = cursor.fetchone()
            print(result)
            if result:
                return result
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
