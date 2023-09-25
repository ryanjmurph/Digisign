
import unittest
from models.User import User

class UserTest(unittest.TestCase):

    created_user_ids = []

    def test_can_create_user(self):
        user = User(name="John Doe", email="johndone1@gmail.com", type="USER")
        user = user.insert()
        self.created_user_ids.append(user.id)
        self.assertIsNotNone(user.id)

    def test_can_find_user(self):
        user = User(name="John Doe", email="johndone2@gmail.com", type="USER")
        user = user.insert()
        self.created_user_ids.append(user.id)

        user = User().findById(user.id)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "johndone2@gmail.com")

    def test_can_find_user_by_email(self):
        user = User(name="John Doe", email="johndone3@gmail.com", type="USER")
        user = user.insert()
        self.created_user_ids.append(user.id)

        user = User().find("johndone3@gmail.com")

        self.assertIsNotNone(user)
        self.assertEqual(user.email,"johndone3@gmail.com")

    def test_user_default_state(self):
        user = User(name="John Doe", email="johndone4@gmail.com", type="USER")
        user = user.insert()

        user = User().findById(user.id)

        self.assertIsNotNone(user)
        self.assertEqual("APPROVAL_REQUIRED", user.state)


    
