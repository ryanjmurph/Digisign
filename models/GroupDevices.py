# Pius Gumo
# 06.09.2023
# PostDevices pivot model to handle the many to many relationship between devices and groups


from models.QueryBuilders.Queries import Query


class PostDevices(Query):

    id = None
    device_id = None
    group_id = None

    def __init__(self, id=None, device_id=None, group_id=None):
        self.id = id
        self.device_id = device_id
        self.group_id = group_id
    
    def associateDevice(self, device_id):
        self.device_id = device_id
        return self


