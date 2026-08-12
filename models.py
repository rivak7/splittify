from __future__ import annotations

import uuid

class User:
    """A simple model of a user."""
    def __init__(self, username: str, user_id: str | None = None):
        self.username = username.strip()
        self._groups = []
        # TODO: Create a registry of active users and their IDs so duplicate
        # IDs passed to the constructor are forbidden
        # TODO: information will eventually be stored/retrieved from JSON
        self.user_id = user_id if user_id is not None else str(uuid.uuid4())

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"User({self.username!r})"

    # TODO: should the return type be int or float?
    def net_balance(self, group: Group | None = None):
        """
        Returns the user's net balance (derived state):
            For all groups if group is None
            For the specified group if group is not None.
        When group.balances[A][B] > 0, User B owes User A money.
        Hence when net_balance() returns a positive number, other users owe this
        user more money than this user owes other users, and vice versa.
        """
        if group is not None:
            return sum(group.balances[self].values())
        overall_net_balance = 0
        for group in self.groups:
            overall_net_balance += sum(group.balances[self].values())
        return overall_net_balance

    @property
    def groups(self):
        # Group.add_users() is the only way to User._groups,
        # enforcing the invariant
        return tuple(self._groups)

class Group:
    """A model for a group of users with debt tracking for split payments."""
    def __init__(self, group_name: str, users: list[User] | None = None):
        """Constructor for a group of users."""
        self.group_name = group_name.strip()
        self._users = []
        self.balances = {}
        if users is not None:
            self.add_users(*users)

    def __str__(self):
        return self.group_name

    def __repr__(self):
        return f"Group({self.group_name!r})"

    def add_users(self, *users):
        for user in users:
            if user in self.users:
                continue # skip duplicates
            # invariant
            self._users.append(user)
            user._groups.append(self)
            # update balances
            self.balances[user] = {}
            for other_user in self.users:
                if other_user != user:
                    self.balances[user][other_user] = 0
                    self.balances[other_user][user] = 0

    @property
    def users(self):
        # enforce the invariant
        return tuple(self._users)
