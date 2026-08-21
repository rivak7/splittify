from .models import User, Group, Expense

class App:
    """Stores app state, including a registry of Users and Groups."""

    def __init__(self, file: str | None = None):
        self.users_by_id = {}
        self.groups_by_id = {}
        if file is not None:
            # TODO: implement initialization using JSON
            pass

    def _users_in_registry(self, *users) -> bool:
        for user in users:
            if self.find_user(user.user_id) is not user:
                return False
        return True

    def _groups_in_registry(self, *groups) -> bool:
        for group in groups:
            if self.find_group(group.group_id) is not group:
                return False
        return True

    def new_user(self, username: str) -> User:
        user = User(username)
        self.users_by_id[user.user_id] = user
        return user

    def new_group(
            self,
            group_name: str,
            users: list[User] | None = None,
    ) -> Group:
        if users is not None:
            if not self._users_in_registry(*users):
                raise ValueError("Unrecognized user(s).")
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
        if not self._groups_in_registry(group):
            raise ValueError("Unrecognized group.")
        if not self._users_in_registry(*users):
            raise ValueError("Unrecognized user(s).")
        group._add_users(*users)

    def add_expense(
        self,
        group: Group,
        payer: User,
        debtors: list[User],
        amount: int,
        description: str,
        split: dict[User, float] | None = None,
        expense_id: str | None = None,
    ) -> Expense:
        if not self._groups_in_registry(group):
            raise ValueError("Unrecognized group.")
        if not self._users_in_registry(payer, *debtors):
            raise ValueError("Unrecognized user(s).")
        return group._add_expense(
            payer,
            debtors,
            amount,
            description,
            split,
            expense_id,
        )

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
