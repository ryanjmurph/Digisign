# Pius Gumo
# 14/08/2023
# Post database model using Pysql

import datetime
from database.database import MYSQL
from models.QueryBuilders.Queries import Query
import qrcode

connection = MYSQL().get_connection()


class Post(Query):
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
    display_time = None

    relationship = {
        "groups": {
            "table": "post_groups_subscription",
            "foreign_key": "post_id",
            "local_key": "id",
        },
    }

    fillable = ["id","title","type","start_date","end_date","image_link","html_content","web_link","state","created_by","created_at","updated_at","display_time"]

    connection = MYSQL().get_connection()

    def __init__(
        self,
        id=None,
        title=None,
        type=None,
        startDate=None,
        endDate=None,
        imageLink=None,
        created_by=None,
        htmlContent=None,
        webLink=None,
        state=None,
        display_time = None
    ) -> None:
        self.id = id
        self.title = title
        self.type = type

        if startDate is not None:
            if isinstance(startDate, datetime.datetime):
                startDate = startDate.strftime("%Y-%m-%d")
            self.start_date = startDate

        if endDate is not None:
            if isinstance(endDate, datetime.datetime):
                endDate = endDate.strftime("%Y-%m-%d")
            self.end_date = endDate

        self.image_link = imageLink
        self.created_by = created_by
        self.html_content = htmlContent
        self.web_link = webLink
        self.state = state
        self.display_time = display_time

    def createInstance(self, result):
        # parse the row into an instance of the post model
        for key in result:
            # set the value of the key to the instance variable
            setattr(self, key, result[key])

            # TODO:// Remove this debug
            # print the instance variable
            # print(f"Setting attribute {key} to {result[key]}")

        return self

    def all(self):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts ORDER BY id DESC LIMIT 30"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def postsWithID(self, id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE id = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result

    def postsCreatedBy(self, id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE created_by = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result

    def no_of_posts(self, user_Id):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM posts WHERE created_by=%s"
            cursor.execute(sql, (user_Id,))
            result = cursor.fetchone()
            if result is not None:
                return result['COUNT(*)']
            else:
                return 0

    def no_of_pending_posts(self, user_Id):
        connection = self.getDatabaseConnection()
        with connection.cursor() as cursor:

            sql = "SELECT COUNT(*) FROM posts WHERE created_by = %s AND state != 'APPROVED'"
            cursor.execute(sql, (user_Id,))
            result = cursor.fetchone()
            if result is not None:
                return result['COUNT(*)']
            else:
                return 0

    def insert(self):
        with connection.cursor() as cursor:
            sql = "INSERT INTO posts (title, type, start_date,end_date,image_link,html_content,web_link,state,created_by,display_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"

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
                    self.created_by,
                    self.display_time
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
        return self

    def remove_groups(self):
        with connection.cursor() as cursor:
            sql = f"DELETE FROM {self.relationship['groups']['table']} WHERE {self.relationship['groups']['foreign_key']} = %s"
            cursor.execute(sql, (self.id))
            connection.commit()

    def save_groups(self, groups):
        self.remove_groups()
        for group in groups:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO {self.relationship['groups']['table']} (post_id, group_id) VALUES (%s, %s)"
                cursor.execute(sql, (self.id, group))
                connection.commit()

    def get_groups(self):
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM {self.relationship['groups']['table']} WHERE {self.relationship['groups']['foreign_key']} = %s"
            cursor.execute(sql, (self.id))
            result = cursor.fetchall()
            return result

    def filter_by_id(self, id):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE id=%s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result

    def filter_by_title(self, title):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE title=%s"
            cursor.execute(sql, (title))
            result = cursor.fetchall()
            return result

    def filter_by_type(self, type):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE type=%s"
            cursor.execute(sql, (type))
            result = cursor.fetchall()
            return result

    def filter_by_state(self, type):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE state=%s"
            cursor.execute(sql, (type))
            result = cursor.fetchall()
            return result

    def filter_start_date(self, start_date):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE start_date=%s"
            cursor.execute(sql, (start_date))
            result = cursor.fetchall()
            return result

    def filter_end_date(self, end_date):
        with connection.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE end_date=%s"
            cursor.execute(sql, (end_date))
            result = cursor.fetchall()
            return result
        
    def get_active_posts(self,query=None,group_ids=None,user_id=None):
        # if no group_ids set and no query set, return all active posts where startDate <= today and endDate >= today
        # if group_ids set and no query set, return all active posts where startDate <= today and endDate >= today and post.id in (SELECT post_id FROM post_groups_subscription WHERE group_id IN (group_ids))

        if type(group_ids) == list:
            # ensure that the group_ids are in a string format and joined by a comma
            group_ids = ",".join([str(id) for id in group_ids])


        if query is not None:
            sql = f"SELECT * FROM posts WHERE (state = 'PUBLISHED' or state = 'APPROVED') AND {query} ORDER BY id DESC"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result 
        elif group_ids is not None:
            sql = f"SELECT * FROM posts WHERE (state = 'PUBLISHED' or state = 'APPROVED') AND id IN (SELECT post_id FROM post_groups_subscription WHERE group_id IN ({group_ids})) ORDER BY id DESC"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        elif user_id is not None:
            sql = f"SELECT * FROM posts WHERE (state = 'PUBLISHED' or state = 'APPROVED') AND created_by = {user_id} ORDER BY id DESC"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        else:
            start_date = datetime.datetime.now().strftime("%Y-%m-%d")
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            sql = f"SELECT * FROM posts WHERE (state = 'PUBLISHED' or state = 'APPROVED') AND start_date <= '{start_date}' AND end_date >= '{end_date}' ORDER BY id DESC"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        
    def get_pending_posts_count(self,query=None,group_ids=None):
        if query is not None:
            sql = f"SELECT COUNT(*) FROM posts WHERE state = 'PENDING' AND {query} "
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                return result["COUNT(*)"]
        elif group_ids is not None:
            sql = f"SELECT COUNT(*) FROM posts WHERE state = 'PENDING' AND id IN (SELECT post_id FROM post_groups_subscription WHERE group_id IN ({group_ids}))"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                return result["COUNT(*)"]
        else:
            sql = "SELECT COUNT(*) FROM posts WHERE state = 'PENDING'"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                return result["COUNT(*)"]

    def associateDevices(self, devices):
        self.device_id = device_id
        return self

    def getDisplayTime(self):
        return self.display_time

    @staticmethod
    def createQR(webLink, code):
        if code:
            qr = qrcode.QRCode(version=1, box_size=5, border=1)
            qr.add_data(webLink)
            qr.make(fit=True)
            img = qr.make_image()
            name = webLink+"qr.jpg"
            img.save("static/images/"+name)
        else:
            file = "static/images/"+webLink+".txt"
            open(file, 'w').close()
