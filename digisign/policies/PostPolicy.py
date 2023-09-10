# Pius Gumo
# 10.09.2023

# Posts policy to enforce controller logic

from models.QueryBuilders.Queries import Query
from models.User import User
from policies.UserPolicy import Policy as UserPolicy


class Policy(UserPolicy,Query):

    def __init__(self, user:User):
        self.user = user
        UserPolicy.__init__(self,user)

    def canViewAllPosts(self):
        return self.isAnAdministator() or self.isAModerator()
    
    def canCreatePost(self):
        return self.isAnAdministator() or (self.isAUser() and self.user.is_active())
    
    def canViewPostList(self):
        return self.isAnAdministator() or (self.isAUser() and self.user.isActive())