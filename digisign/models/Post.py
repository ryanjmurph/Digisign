# Pius Gumo
# 14/08/2023
# Post database model using Pysql

from datetime import datetime
from database.database import MYSQL

connection = MYSQL().get_connection()


class Post:
    id = None
    title = None
    type = None
    start_date = None
    end_date = None
    image_link = None
    html_content = None
    web_link = None
    state = "DRAFT"
    created_by = None
    created_at = None
    updated_at = None

    def __init__(
        self,
        id=None,
        title=None,
        type=None,
        startDate=None,
        endDate=None,
        imageLink=None,
        htmlContent=None,
        webLink=None,
        state=None,
    ) -> None:
        self.id = id
        self.title = title
        self.type = type
        self.start_date = startDate
        self.end_date = endDate
        self.image_link = imageLink
        self.html_content = htmlContent
        self.web_link = webLink
        self.state = state

    def createInstance(self, result):
        # parse the row into an instance of the post model
        for key in result:
            # set the value of the key to the instance variable
            setattr(self, key, result[key])

            # TODO:// Remove this debug
            # print the instance variable
            # print(f"Setting attribute {key} to {result[key]}")

        return self

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts ORDER BY id DESC LIMIT 30"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def find(id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchone()
            # return instance of the post
            return Post().createInstance(result)

    def insert(self):
        with connection.cursor() as cursor:
            sql = "INSERT INTO posts (title, type, start_date,end_date,image_link,html_content,web_link,state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            cursor.execute(
                sql,
                (
                    self.title,
                    self.type,
                    self.start_date,
                    self.end_date,
                    self.image_link,
                    self.html_content,
                    self.web_link,
                    self.state,
                ),
            )
            connection.commit()
            self.id = cursor.lastrowid
        return self

    def updates(self, changes):
        # Changes is a dict containing the changes to be made
        # e.g. changes = {"title": "New Title", "state": "APPROVED"}

        # Check through the changes dict and build the sql query to update the post
        sql = "UPDATE posts SET "
        for key in changes:
            sql += f"{key}=%s, "
        sql = sql[:-2]  # remove the last comma and space
        sql += " WHERE id=%s"

        # create a list of values to be updated
        values = []
        for key in changes:
            values.append(changes[key])
        values.append(self.id)

        # execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            connection.commit()

        # return the updated post
        return Post.find(self.id)

    def save_groups(self, groups):
        for group in groups:
            with connection.cursor() as cursor:
                sql = "INSERT INTO post_group (post_id, group_id) VALUES (%s, %s)"
                cursor.execute(sql, (self.id, group))
                connection.commit()

    def filter_by_id(id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result

    def filter_by_title(title):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE title=%s"
            cursor.execute(sql, (title))
            result = cursor.fetchall()
            return result

    def filter_by_type(type):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE type=%s"
            cursor.execute(sql, (type))
            result = cursor.fetchall()
            return result

    def filter_by_state(type):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE state=%s"
            cursor.execute(sql, (type))
            result = cursor.fetchall()
            return result

    def filter_start_date(start_date):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE start_date=%s"
            cursor.execute(sql, (start_date))
            result = cursor.fetchall()
            return result

    def filter_end_date(end_date):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE end_date=%s"
            cursor.execute(sql, (end_date))
            result = cursor.fetchall()
            return result
