# Pius Gumo
# 06.09.2023
# PostDevices pivot model to handle the many to many relationship between devices and groups


from database.database import MYSQL
from models.QueryBuilders.Queries import Query


class GroupDevices(Query):

    id = None
    device_id = None
    group_id = None

    connection = MYSQL().get_connection()

    table_name = "group_device_subscriptions"

    fillable = ["device_id","group_id"]

    def __init__(self, id=None, device_id=None, group_id=None):
        self.id = id
        self.device_id = device_id
        self.group_id = group_id
    
    def associateDevice(self, device_id):
        self.device_id = device_id
        return self
    
    def get_groups_for_device(self, device_id):
        self.device_id = device_id
        sql = f"""
            SELECT {self.table_name}.*,post_groups.color
            from {self.table_name}
            JOIN post_groups ON {self.table_name}.group_id = post_groups.id
            WHERE {self.table_name}.device_id = {self.device_id}"""        
        results = self.raw(sql)

        return results