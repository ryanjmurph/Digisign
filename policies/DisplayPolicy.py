
from models.User import User


class Policy():

    user = None

    def __init__(self,user:User):
        self.user = user

    def can_view_displays(self):
        return self.user.get_type() == "DEVICE"
    
        
