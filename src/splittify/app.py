from .models import User, Group

class App:
    """Stores app state, including a registry of Users and Groups."""

    def __init__(self, file: str | None = None):
        self.users_by_id = {}
        self.groups_by_id = {}
        if file is not None:
            # TODO: implement initialization using JSON
            pass

    def new_user(self, username: str) -> User:
        user = User(username)
        self.users_by_id[user.user_id] = user
        return user

    def new_group(
            self,
            group_name: str,
            users: list[User] | None = None,
    ) -> Group:
        # Any user passed into App operations must belong to the user registry
        if users is not None:
            for user in users:
                if self.find_user(user.user_id) is not user:
                    raise ValueError("Unrecognized user.")
        group = Group(group_name, users)
        self.groups_by_id[group.group_id] = group
        return group

    def find_user(self, user_id: str) -> User | None:
        try:
            return self.users_by_id[user_id]
        except KeyError:
            return None

    def find_group(self, group_id: str) -> Group | None:
        try:
            return self.groups_by_id[group_id]
        except KeyError:
            return None

    def add_users_to_group(self, group, *users):
        if self.find_group(group.group_id) is not group:
            raise ValueError("Unrecognized group.")
        for user in users:
            if self.find_user(user.user_id) is not user:
                raise ValueError("Unrecognized user.")
        group._add_users(*users)

    def add_expense(self, group, expense):
        pass

    # TODO: decide if/how to implement deletion methods
    def delete_user(self, user_id: str):
        # how to deal with existing debts?
        # must delete user from groups (also consider what to do w/ User.groups)

        # maybe deleting a user is only allowed when all edges connected to the
        # user in all balance graphs are zero (debts fully settled)
        raise NotImplementedError()

    def delete_group(self, group_id: str):
        # maybe deleting a group is only allowed when all edges in its balance
        # graph are zero (debts fully settled)
        raise NotImplementedError()

    # TODO: implement JSON and JSON-dependent functionalities
