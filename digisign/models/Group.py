# Pius Gumo
# 14/08/2023
# Groups model using Pysql. 

import datetime
from database.database import MYSQL

connection = MYSQL().get_connection()


class Group:

    id = None
    name = None
    description = None
    moderation_required = False
    created_at = None
    updated_at = None

    def __init__(self,name,description) -> None:
        self.name = name
        self.description = description
        self.created_at = datetime.now().strftime("%Y-%m-%d")
        self.updated_at = datetime.now().strftime("%Y-%m-%d")

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM post_groups"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result