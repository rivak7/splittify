"""Unit tests for the application state and entity registries in Splittify."""

import unittest

from app import App
from models import User, Group


class TestApp(unittest.TestCase):
    """Test case for the App class."""

    def setUp(self):
        self.app = App()

    def test_new_user_is_registered(self):
        alice = self.app.new_user("Alice")
        self.assertIs(self.app.find_user(alice.user_id), alice)

    def test_new_users_have_different_ids(self):
        alice = self.app.new_user("Alice")
        bob = self.app.new_user("Bob")
        self.assertNotEqual(alice.user_id, bob.user_id)

    def test_new_group_is_registered(self):
        alice = self.app.new_user("Alice")
        bob = self.app.new_user("Bob")
        group = self.app.new_group("Trip", [alice, bob])
        self.assertIs(self.app.find_group(group.group_id), group)

    def test_group_membership_is_bidirectional(self):
        alice = self.app.new_user("Alice")
        bob = self.app.new_user("Bob")
        group = self.app.new_group("Trip", [alice, bob])
        self.assertIn(alice, group.users)
        self.assertIn(bob, group.users)
        self.assertIn(group, alice.groups)
        self.assertIn(group, bob.groups)

    def test_supplied_ids_are_preserved(self):
        user = User("Alice", user_id="0")
        group = Group("Trip", group_id="1")
        self.assertEqual(user.user_id, "0")
        self.assertEqual(group.group_id, "1")


if __name__ == "__main__":
    unittest.main()
