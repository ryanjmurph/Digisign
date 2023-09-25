import unittest

from app import app
from models.Post import Post
from models.User import User

import datetime

class PostTest(unittest.TestCase):
    def setUp(self) -> None:
        # create user
        user = User(email="Test_Account", password="Test_Password", name="Test Account",
                type="USER", state="APPROVAL_REQUIRED")
        user = user.insert()
        self.user = user


    def test_create_post(self):
        post = Post(title='Test Post',type="HTML",state="PUBLISHED", htmlContent='This is a test post', created_by=self.user.id)
        post = post.save()
        self.assertIsNotNone(post.id)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.type, 'HTML')
        self.assertEqual(post.state, 'PUBLISHED')
        self.assertEqual(post.html_content, 'This is a test post')
        self.assertEqual(post.created_by, self.user.id)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_retreive_post(self):
        post = Post(title='Test Post',type="HTML",state="PUBLISHED", htmlContent='This is a test post', created_by=self.user.id)
        post = post.save()
        post = Post().find(post.id)
        self.assertIsNotNone(post.id)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.type, 'HTML')
        self.assertEqual(post.state, 'PUBLISHED')
        self.assertEqual(post.html_content, 'This is a test post')
        self.assertEqual(post.created_by, self.user.id)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_delete_user_delete_post(self):
        # create a new test user, delete it, and try to find the post
        user = User(email="Test_Account_2", password="Test_Password", name="Test Account",
                type="USER", state="APPROVED")
        user = user.insert()
        post = Post(title='Test Post',type="HTML",state="PUBLISHED", htmlContent='This is a test post', created_by=user.id)
        post = post.save()

        # delete the user
        user.delete()

        # try to find the post
        post = Post().find(post.id)

        # post should be None
        self.assertIsNone(post)

    def test_expired_posts(self):
        # create a post who's start and end dates are in the past
        past_post = Post(title='Test Post',type="HTML",state="PUBLISHED", htmlContent='This is a test post', created_by=self.user.id, startDate="2021-01-01", endDate="2021-01-02")
        past_post = past_post.save()

        active_posts = Post().get_active_posts()
        active_posts = [post['id'] for post in active_posts]

        # post should not be in the list of active posts
        self.assertNotIn(past_post.id, active_posts)
    
    def test_unpublished_posts(self):
        post = Post(title='Test Post',type="HTML",state="DRAFT", htmlContent='This is a test post', created_by=self.user.id)
        post = post.save()

        active_posts = Post().get_active_posts()
        active_posts = [post['id'] for post in active_posts]

        # post should not be in the list of active posts
        self.assertNotIn(post.id, active_posts)

    def test_future_posts(self):
        startDateFuture = datetime.datetime.now() + datetime.timedelta(days=1)
        endDateFuture = datetime.datetime.now() + datetime.timedelta(days=2)

        post = Post(title='Test Post',type="HTML",state="PUBLISHED", htmlContent='This is a test post', created_by=self.user.id, startDate=startDateFuture, endDate=endDateFuture)
        post = post.save()

        active_posts = Post().get_active_posts()
        active_posts = [post['id'] for post in active_posts]

        # post should not be in the list of active posts
        self.assertNotIn(post.id, active_posts)

    def tearDown(self) -> None:
        # delete user
        self.user.delete()
        pass
