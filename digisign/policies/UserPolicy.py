# Pius Gumo
# 10.09.2023

# user policy to enforce controller logic

from models.GroupModerator import GroupModerator
from models.QueryBuilders.Queries import Query


class Policy(Query):

    user = None

    isModerator = None

    def __init__(self,user):
        self.user = user

    def canViewAllUsers(self):
        return self.isAnAdministator()
    
    def canviewAllGroups(self):
        return self.isAnAdministator()
    
    def canViewAllPosts(self):
        return self.isAnAdministator()
    
    def canCreateDevice(self):
        return self.isAnAdministator()
    

    
    # A user can only edit their own profile or if they are an administrator
    def canEditUser(self,user_id):
        if self.user.type == "ADMINISTRATOR":
            return True
        return self.user.id == user_id
    
    def getGroupsCanModerate(self):
        if self.available_groups == None:
            available_groups = GroupModerator(user=self.user).getGroupsCanModerate()
            self.available_groups = available_groups
        return self.available_groups
    
    def checkDatabaseIfUserIsModerator(self):
        if len(self.getGroupsCanModerate()) == 0:
            return False
        return True

    def isAnAdministator(self):
        return self.user.type == "ADMINISTRATOR"
    
    def isAUser(self):
        return self.user.type == "USER"
    
    def isADevice(self):
        return self.user.type == "DEVICE"
    
    def isAModerator(self):
        if self.isModerator == None:
            self.isModerator = self.checkDatabaseIfUserIsModerator()
        return self.isModerator

            
        
