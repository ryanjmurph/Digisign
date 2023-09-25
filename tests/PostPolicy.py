import unittest
from models.User import User
from models.Post import Post
from models.Group import Group
from policies.PostPolicy import Policy


class TestPostPolicy(unittest.TestCase):

    def setUp(self):
        user = User(id=1, name="John Doe", email="john.doe@example.com", type="USER")
        self.user = user.insert()
        self.policy = Policy(user=self.user)
    
    def tearDown(self) -> None:
        self.user.delete()

    def test_can_view_all_posts(self):
        # admin can view all posts
        self.user.type = "ADMINISTRATOR"
        self.assertTrue(self.policy.canViewAllPosts())

    def moderator_cannot_view_all_posts(self):
        # moderator cannot view all posts
        self.user.type = "MODERATOR"
        self.assertFalse(self.policy.canViewAllPosts())
    
    def user_cannot_view_all_posts(self):
        # user cannot view all posts
        self.user.type = "USER"
        self.assertFalse(self.policy.canViewAllPosts())

    def device_cannot_view_all_posts(self):
        # device cannot view all posts
        self.user.type = "DEVICE"
        self.assertFalse(self.policy.canViewAllPosts())

    def test_can_create_post(self):
        self.user.type = "USER"
        self.assertTrue(self.policy.canCreatePost())

    def test_device_cannot_create_post(self):
        self.user.type = "DEVICE"
        self.assertFalse(self.policy.canCreatePost())


    def test_admin_can_approve_post(self):
        post = Post(id=1, title="Test Post", htmlContent="This is a test post", created_by=-100)
        self.user.type = "ADMINISTRATOR"
        self.assertTrue(self.policy.canApprovePost(post))
    
    def test_moderator_can_approve_post(self):
        another_user = User(id=2, name="Jane Doe", email="moderator@gmail.com", type="USER")
        another_user = another_user.insert()

        group = Group(name="Test Group")
        group = group.save()

        # add another user as moderator
        group.add_moderator(another_user.id)

        post = Post(title="Test Post", htmlContent="This is a test post")
        post = post.save()

        # add post to group
        group.add_post(post.id)

        # remove the other user
        another_user.delete()

    def test_can_manage_post(self):
        post = Post(id=1, title="Test Post", htmlContent="This is a test post", created_by=self.user.id)
        self.assertTrue(self.policy.canManagePost(post))

    def test_can_edit_post(self):
        post = Post(id=1, title="Test Post", htmlContent="This is a test post", created_by=self.user.id)
        self.assertTrue(self.policy.canEditPost(post))