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

    def __init__(self,id,title,type,startDate,endDate,imageLink,htmlContent,webLink,state) -> None:
        self.id = id
        self.title = title
        self.type = type
        self.startDate = startDate
        self.endDate = endDate
        self.imageLink = imageLink
        self.htmlContent = htmlContent
        self.webLink = webLink
        self.state = state



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
            sql = "INSERT INTO post (title, type, start_date,end_date,image_link,html_content,web_link,state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
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
