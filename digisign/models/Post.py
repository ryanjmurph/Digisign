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

        # log the details of the post
        print(
            f"Post: {self.title}, Type: {self.type}, Start Date: {self.start_date}, End Date: {self.end_date}, Image Link: {self.image_link}, HTML Content: {self.html_content}, Web Link: {self.web_link}, State: {self.state}"
        )

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM post"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def find(id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM post WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchone()
            return result

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

    def save_groups(self, groups):
        for group in groups:
            with connection.cursor() as cursor:
                sql = "INSERT INTO post_group (post_id, group_id) VALUES (%s, %s)"
                cursor.execute(sql, (self.id, group))
                connection.commit()
