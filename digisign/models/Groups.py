# Pius Gumo
# 14/08/2023
# Groups model using Pysql. 

import datetime


class Groups:

    id = None
    name = None
    description = None
    created_at = None
    updated_at = None

    def __init__(self,name,description) -> None:
        self.name = name
        self.description = description
        self.created_at = datetime.now().strftime("%Y-%m-%d")
        self.updated_at = datetime.now().strftime("%Y-%m-%d")

    def all():
        with connection.cursor() as cursor:
            sql = "SELECT * FROM groups"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result