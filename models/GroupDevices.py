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

    def __init__(self, id=None, device_id=None, group_id=None):
        self.id = id
        self.device_id = device_id
        self.group_id = group_id
    
    def associateDevice(self, device_id):
        self.device_id = device_id
        return self
    
    def get_groups_for_device(self, device_id):
        self.device_id = device_id        
        results = self.raw(f"SELECT * FROM {self.table_name} WHERE device_id = '{self.device_id}'")

        print(results)

        group_ids = [res["group_id"] for res in results]
        return group_ids