# Pius Gumo
# 14/08/2023
# Post database model using Pysql

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
    display_time = None
    created_by = None
    created_at = None
    updated_at = None

    relationship = {
        "groups": {
            "table": "post_groups_subscription",
            "foreign_key": "post_id",
            "local_key": "id",
        },
    }

    fillable = ["id","title","type","start_date","end_date","image_link","html_content","web_link","state","display_time","created_by","created_at","updated_at"]

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
        display_time = None,
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
        self.created_by = created_by
        self.display_time = display_time
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
            sql = "INSERT INTO posts (title, type, start_date,end_date,image_link,html_content,web_link,state,created_by, display_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"

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
        return Post.find(self.id)

    def save_groups(self, groups):
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

    def getDisplayTimesFromDB(self,id):
        with connection.cursor() as cursor:
            sql = "SELECT display_time FROM posts WHERE id = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result  
        
    def getIDFromFileName(self,fileName):
        result = ""
        for letter in fileName:
            if(letter!= "_"):
                result = result + letter
            else:
                break
        return int(result)
    
    
    def associateDevices(self, devices):
        self.device_id = device_id
        return self
    
    @property
    def get_display_time(self):
        return int(self.display_time)
    

    def get_id(self):
        return self.id

    @staticmethod
    def createQR(webLink,code,id):
        stringId = str(id)
        if code:
            qr = qrcode.QRCode(version = 1, box_size = 5, border =1)
            qr.add_data(webLink)
            qr.make(fit = True)
            img = qr.make_image()
            name = stringId + "_"+ webLink+"qr.jpg"
            img.save("static/images/"+name)
        else:
            file = "static/images/"+ stringId + "_"+webLink+".txt"
            open(file, 'w').close()