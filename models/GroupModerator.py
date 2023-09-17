

from database.database import MYSQL
from models.Group import Group
from models.QueryBuilders.Queries import Query
from models.User import User


class GroupModerator(Query):

    # table_name = "post_groups"
    connection = MYSQL().get_connection()

    def __init__(self,group=None,user=None,current_moderators=None):
        self.group = group
        self.user = user
        self.current_moderators = current_moderators

    def getGroupsCanModerate(self):
        if not self.user:
            return Exception("User must be set")
        
        with self.connection.cursor() as cursor:
            sql = f"SELECT group_id FROM {self.getTableName()} WHERE user_id = {self.user.id}"
            print(f"SQL: {sql}")
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getCurrentModerators(self):
        if not self.current_moderators:
            self.current_moderators = self.group.getModerators()

        return self.current_moderators

    def isUserModerator(self):
        user_id = self.user.id
        current_moderators = self.getCurrentModerators()

        for moderator in current_moderators:
            if moderator["id"] == user_id:
                return True
        return False
    
    def addModerator(self):
        if not self.isUserModerator():
            with self.connection.cursor() as cursor:
                sql = f"INSERT INTO group_moderators(group_id,user_id) VALUES({self.group.id},{self.user.id})"
                cursor.execute(sql)
                self.connection.commit()
                return True
        print(f"{self.user.name} is already a moderator of {self.group.name}")
        return False
    
    def removeModerator(self):
        if self.isUserModerator():
            with self.connection.cursor() as cursor:
                sql = f"DELETE FROM group_moderators WHERE group_id = {self.group.id} AND user_id = {self.user.id}"
                cursor.execute(sql)
                self.connection.commit()
                return True
        return False
    
    

    