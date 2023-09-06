# Pius Gumo
# 14/08/2023
# Groups model using Pysql. 

from database.database import MYSQL
from models.Queries import Query


class Group(Query):

    id = None
    name = None
    description = None
    moderation_required = False
    created_at = None
    updated_at = None

    table_name = "post_groups"
    connection = MYSQL().get_connection()

    casts = { "moderation_required" : "bool" }

    def __init__(self,name=None,description=None,moderation_required=None) -> None:
        self.name = name
        # self.description = description 
        self.moderation_required = moderation_required


    def all(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM post_groups"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        
    def getPostsCount(self,group_id):
        with self.connection.cursor() as cursor:
            sql = f"SELECT COUNT(*) as count FROM post_groups_subscription WHERE group_id = {group_id}"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result["count"]