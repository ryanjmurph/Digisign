from datetime import datetime

from flask_login import UserMixin
from database.database import MYSQL
from models.QueryBuilders.Queries import Query


class User(Query):
    id = None
    name = None
    email = None
    password = None
    state = None
    type = None
    created_at = None
    updated_at = None

    connection = MYSQL().get_connection()

    fillable = ["name", "email", "password",
                "type", "state", "created_at", "updated_at"]

    def __init__(
        self,
        id=None,
        name=None,
        email=None,
        password=None,
        type=None,
        created_at=None,
        updated_at=None,
        state=None,

    ) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.state = state

    def all(self):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def find(self, email):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email))
            result = cursor.fetchone()
            if result:
                return self.setPropertiesOfUser(result)
            else:
                return None

    def isModerator(self, id=None):
        if id is None:
            id = self.id
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM group_moderators WHERE user_id = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result[0]['count'] > 0

    def findById(self, id):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchone()
            if result:
                return self.setPropertiesOfUser(result)
            else:
                return None

    def insert(self):
        connection = self.getDatabaseConnection()
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
        self.state = user["state"]
        self.type = user["type"]
        self.created_at = user["created_at"]
        self.updated_at = user["updated_at"]
        return self

    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

    def is_active(self):
        return self.state == "ACTIVE"

    def get_id(self):
        return str(self.id)

    def get_email(self):
        return str(self.email)

    def get_type(self):
        return str(self.type)

    def get_state(self):
        return str(self.state)

    def get_password(self):
        return str(self.password)
    
    def get_pending_users(self):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE state = 'APPROVAL_REQUIRED'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "type": self.type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state,
        }
