# Pius Gumo
# 10.09.2023

# user policy to enforce controller logic

from models.GroupModerator import GroupModerator
from models.QueryBuilders.Queries import Query


class Policy(Query):
    """
    A class that defines the user policy to enforce controller logic.
    """

    user = None

    isModerator = None

    def __init__(self,user):
        """
        Initializes the Policy class with a user object.

        Args:
        - user: A user object.
        """
        self.user = user

    def can_create_user(self):
        """
        Checks if the user can create a new user.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()

    def canViewAllUsers(self):
        """
        Checks if the user can view all users.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()
    
    def canviewAllGroups(self):
        """
        Checks if the user can view all groups.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()
    
    def canViewAllPosts(self):
        """
        Checks if the user can view all posts.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()
    
    def canCreateDevice(self):
        """
        Checks if the user can create a new device.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()
    
    def canApproveUsers(self):
        """
        Checks if the user can approve users.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()
    
    def canEditUser(self,user_id):
        """
        Checks if the user can edit a user.

        Args:
        - user_id: The ID of the user to be edited.

        Returns:
        - True if the user is an administrator or the user to be edited is the same as the current user, False otherwise.
        """
        if self.user.type == "ADMINISTRATOR":
            return True
        return self.user.id == user_id
    
    def getGroupsCanModerate(self):
        """
        Gets the groups that the user can moderate.

        Returns:
        - A list of groups that the user can moderate.
        """
        if self.available_groups == None:
            available_groups = GroupModerator(user=self.user).getGroupsCanModerate()
            self.available_groups = available_groups
        return self.available_groups
    
    def checkDatabaseIfUserIsModerator(self):
        """
        Checks if the user is a moderator.

        Returns:
        - True if the user is a moderator, False otherwise.
        """
        if len(self.getGroupsCanModerate()) == 0:
            return False
        return True
    
    def isAnAdministator(self):
        """
        Checks if the user is an administrator.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.user.type == "ADMINISTRATOR"
    
    def isAUser(self):
        """
        Checks if the user is a regular user.

        Returns:
        - True if the user is a regular user, False otherwise.
        """
        return self.user.type == "USER"
    
    def isADevice(self):
        """
        Checks if the user is a device.

        Returns:
        - True if the user is a device, False otherwise.
        """
        return self.user.type == "DEVICE"
    
    def isAModerator(self):
        """
        Checks if the user is a moderator.

        Returns:
        - True if the user is a moderator, False otherwise.
        """
        if self.user.isModerator(self.user.id) == 0:
            return False
        else:
            return True

            
        
