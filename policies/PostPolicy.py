# Pius Gumo
# 10.09.2023

# Posts policy to enforce controller logic

from models.GroupModerator import GroupModerator
from models.Post import Post
from models.QueryBuilders.Queries import Query
from models.User import User
from policies.UserPolicy import Policy as UserPolicy


class Policy(UserPolicy, Query):
    """
    This class defines the policies for posts in the system.
    It inherits from UserPolicy and Query classes.
    """

    user: User = None

    def __init__(self, user: User):
        """
        Initializes the Policy class with a user object.

        Args:
        - user: A User object representing the user whose policies are being defined.
        """
        self.user = user
        UserPolicy.__init__(self, user)

    def postRequiresAnyApproval(self, post: Post):
        """
        Checks if a post requires any approval.

        Args:
        - post: A Post object representing the post to be checked.

        Returns:
        - True if the post requires approval, False otherwise.
        """
        groups = post.get_groups()
        for group in groups:
            if group["requires_approval"]:
                return True
        return False

    def canViewAllPosts(self):
        """
        Checks if the user can view all posts.

        Returns:
        - True if the user is an administrator or moderator, False otherwise.
        """
        return self.isAnAdministator() or self.isAModerator()

    def can_view_moderator_posts(self):
        """
        Checks if user is a moderator
        """
        return self.isAModerator()

    def canCreatePost(self):
        """
        Checks if the user can create a post.

        Returns:
        - True if the user is an administrator or a user who is active, False otherwise.
        """
        return self.isAnAdministator() or (self.isAUser() and self.user.is_active())

    def canViewAdminPostList(self):
        """
        Checks if the user can view the admin post list.

        Returns:
        - True if the user is an administrator, False otherwise.
        """
        return self.isAnAdministator()

    def canViewPostList(self):
        """
        Checks if the user can view the post list.

        Returns:
        - True if the user is a user who is active, False otherwise.
        """
        return self.isAUser() and self.user.is_active()

    def canApprovePost(self, post:Post):
        """
        Checks if the user can approve a post.

        Args:
        - post: A Post object representing the post to be approved.

        Returns:
        - True if the user is a moderator who can moderate the post's group or an administrator, False otherwise.
        """
        if self.user.isModerator():
            groups = GroupModerator(user=self.user).getGroupsCanModerate()
            post_groups = post.get_groups()
            groups = [group["group_id"] for group in groups]
            post_groups = [group["group_id"] for group in post_groups]
            for group in post_groups:
                if group in groups:
                    return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False

    def canManagePost(self, post):
        """
        Checks if the user can manage a post. Managing is either 
        approving / rejecting the post or deleting the post.

        Args:
        - post: A Post object representing the post to be managed.

        Returns:
        - True if the user created the post, is a moderator who can moderate the post's group or an administrator, False otherwise.
        """
        if post.created_by == self.user.id:
            return True
        if self.user.isModerator():
            groups = GroupModerator(user=self.user).getGroupsCanModerate()
            post_groups = post.get_groups()
            groups = [group["group_id"] for group in groups]
            post_groups = [group["group_id"] for group in post_groups]
            print("Groups can moderate: ", groups)
            print("Post groups: ", post_groups)
            for group in post_groups:
                if group in groups:
                    return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False

    def canEditPost(self, post):
        """
        Checks if the user can edit a post.

        Args:
        - post: A Post object representing the post to be edited.

        Returns:
        - True if the user created the post or is an administrator, False otherwise.
        """
        if post.created_by == self.user.id:
            return True
        if UserPolicy(self.user).isAnAdministator():
            return True
        return False
