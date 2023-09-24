# Pius Gumo
# 14/08/2023
# Groups model using Pysql. 

from database.database import MYSQL
from models.QueryBuilders.Queries import Query


class Group(Query):

    id = None
    name = None
    description = None
    moderation_required = False
    created_at = None
    updated_at = None

    table_name = "post_groups"
    connection = MYSQL().get_connection()

    fillable = ["name", "description", "moderation_required"]

    casts = { "moderation_required" : "bool" }
    relationship = {
        "devices": {
            "table": "group_device_subscriptions",
            "foreign_key": "group_id",
            "local_key": "id",
            "eager_load":{
                "table": "users",
                "foreign_key": "device_id",
                "local_key": "id",
                "columns": "id,name"
            },
        },
        "posts": {
            "table": "post_groups_subscription",
            "foreign_key": "group_id",
            "local_key": "id",
        },
        "moderators": {
            "table": "group_moderators",
            "foreign_key": "group_id",
            "local_key": "id",
            "eager_load":{
                "table": "users",
                "foreign_key": "user_id",
                "local_key": "id",
                "columns": "id,email,name"
            },
        },
    }

    def __init__(self,name=None,description=None,moderation_required=None) -> None:
        self.name = name
        self.description = description 
        self.moderation_required = moderation_required


    @classmethod
    def all(cls):
        with cls.connection.cursor() as cursor:
            sql = "SELECT * FROM post_groups"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
   
    def groupByModerator(self, id): # the group ids moderated by user with id 
        with self.connection.cursor() as cursor:
            sql = "SELECT group_id FROM group_moderators WHERE user_id = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result
        
    def getGroupWithID(self, id): # the group info using the group ids
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM post_groups WHERE id = %s"
            cursor.execute(sql, (id))
            result = cursor.fetchall()
            return result

    def getPostsCount(self,group_id):
        with self.connection.cursor() as cursor:
            sql = f"SELECT COUNT(*) as count FROM post_groups_subscription WHERE group_id = {group_id}"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result["count"]
        
    def getDevicesAssociatedWithGroup(self,columns="*"):
        relationship = self.relationship["devices"]
        columns = ",".join(columns)
        with self.connection.cursor() as cursor:
            sql = f"SELECT {columns} FROM {relationship['table']} WHERE {relationship['foreign_key']} = {self.id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        
        
    def associateDevicesWithGroup(self,devices):
        devices_not_associated_with_group = []
        devices_associated_with_group = []

        # get the devices associated with the group
        devices_associated_with_group = self.getDevicesAssociatedWithGroup(['id','device_id'])

        # get devices that are not associated with the group
        for device in devices:
            if device not in devices_associated_with_group:
                devices_not_associated_with_group.append(device)

        relationship_table = self.relationship["devices"]["table"]

        # associate the devices with the group
        if len(devices_not_associated_with_group) > 0:
            with self.connection.cursor() as cursor:
                sql = f"INSERT INTO {relationship_table} (group_id,device_id) VALUES "
                for device in devices_not_associated_with_group:
                    sql += f"({self.id},{device}),"
                sql = sql[:-1]
                cursor.execute(sql)
                self.connection.commit()

    def getModeratorss(self,eager_load=False):
        relationship = self.relationship["moderators"]
        if not eager_load:
            with self.connection.cursor() as cursor:
                sql = f"SELECT * FROM {relationship['table']} WHERE {relationship['foreign_key']} = {self.id}"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        else:
            with self.connection.cursor() as cursor:
                sql = f"\
                        SELECT {relationship['eager_load']['columns']} FROM {relationship['table']} INNER JOIN {relationship['eager_load']['table']} ON {relationship['table']}.{relationship['eager_load']['foreign_key']} = {relationship['eager_load']['table']}.{relationship['eager_load']['local_key']} WHERE {relationship['table']}.{relationship['foreign_key']} = {self.id}\
                            "
                print(sql)
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
            
    def getModerators(self):
        relationship = self.relationship["moderators"]
        sql = self.withRelation(relationship["eager_load"],fromTable=relationship["table"],fromTableForeignKey=relationship["foreign_key"])
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        
    def get_devices(self):
        relationship = self.relationship["devices"]
        sql = self.withRelation(relationship["eager_load"],fromTable=relationship["table"],fromTableForeignKey=relationship["foreign_key"])
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
