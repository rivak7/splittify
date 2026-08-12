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

    def net_balance(self):
        """
        Returns the user's net balance (derived state) across all groups it is
        a member of. Positive net_balance means that other users owe this user
        more money than this user owes other users, and vice versa.
        """
        # TODO: Derive the net balance by accessing group details
        # and calculating the net balance for each group, then summing them.

        raise NotImplementedError()

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
