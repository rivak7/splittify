class User:
    """A simple model of a user."""
    def __init__(self, name: str):
        self.name = name.strip()
        self.groups = []

    def add_to_groups(self, *groups):
        # FIXME: when the same group is added twice, things may break.
        # Consider using a set, may cause hashability issues down the line
        self.groups.extend(groups)

    def net_balance(self):
        """
        Returns the user's net balance (derived state) across all groups it is
        a member of. Positive net_balance means that other users owe this user
        more money than this user owes other users, and vice versa.
        """
        # TODO: Update the net balance by accessing group details
        # and calculating the net balance for each group, then summing them.

        return net_balance

class Group:
    """A model for a group of users with debt tracking for split payments."""
    def __init__(self, users: list[User] | None = None):
        """Constructor for a group of users."""
        # TODO: balances should be tracked as a dictionary of dictionaries.
        # This makes net_balance easy to implement.
