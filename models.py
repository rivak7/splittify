from __future__ import annotations

import uuid

class User:
    """A simple model of a user."""
    def __init__(self, username: str, user_id: str | None = None):
        """
        This constructor is for use by an App instance only. A new User
        should not be created using User(); instead, use App.new_user().
        """
        self._user_id = user_id if user_id is not None else str(uuid.uuid4())
        self.username = username.strip()
        self._groups = []

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"User({self.username!r})"

    # TODO: should the return type be int or float?
    def net_balance(self, group: Group | None = None):
        """
        Returns the user's net balance (derived state):
            For all groups if group is None,
            For the specified group if group is not None.
        When group.balances[A][B] > 0, User B owes User A money.
        Invariant: balances[A][B] = -balances[B][A].
        When net_balance() returns a positive number, other users owe this
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
        # Group.add_users() is the only way to modify User._groups,
        # enforcing the invariant
        return tuple(self._groups)

    @property
    def user_id(self):
        return self._user_id


class Group:
    """A model for a group of users with debt tracking for split payments."""
    def __init__(
        self,
        group_name: str,
        users: list[User] | None = None,
        group_id: str | None = None,
    ):
        """
        This constructor is for use by an App instance only. A new Group
        should not be created using Group(); instead, use App.new_group().
        """
        self._group_id = group_id if group_id is not None else str(uuid.uuid4())
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

    @property
    def group_id(self):
        return self._group_id
