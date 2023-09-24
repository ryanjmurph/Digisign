# Pius Gumo
# 10.09.2023

# Posts policy to enforce controller logic

from models.GroupModerator import GroupModerator
from models.Post import Post
from models.QueryBuilders.Queries import Query
from models.User import User
from policies.UserPolicy import Policy as UserPolicy


class Policy(UserPolicy, Query):

    user: User = None

    def __init__(self, user: User):
        self.user = user
        UserPolicy.__init__(self, user)

    def postRequiresAnyApproval(self, post: Post):
        groups = post.get_groups()
        for group in groups:
            if group["requires_approval"]:
                return True
        return False

    def canViewAllPosts(self):
        return self.isAnAdministator() or self.isAModerator()

    def canCreatePost(self):
        return self.isAnAdministator() or (self.isAUser() and self.user.is_active())

    def canViewAdminPostList(self):
        return self.isAnAdministator()

    def canViewPostList(self):
        return self.isAUser() and self.user.is_active()

    def canApprovePost(self, post:Post):
        if self.user.isModerator():
            groups = GroupModerator(user=self.user).getGroupsCanModerate()
            post_groups = post.get_groups()
            for group in post_groups:
                if group["id"] in groups:
                    return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False

    def canManagePost(self, post):
        if post.created_by == self.user.id:
            return True
        if self.user.isModerator():
            groups = GroupModerator(user=self.user).getGroupsCanModerate()
            if post.group_id in groups:
                return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False

    def canEditPost(self, post):
        if post.created_by == self.user.id:
            return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False
