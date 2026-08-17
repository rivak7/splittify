"""Models for Users and Groups of Users in Splittify App instances."""

from __future__ import annotations
# from dataclasses import dataclass, field
from datetime import datetime, timezone
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

    def net_balance(self, group: Group | None = None) -> int:
        """
        Returns the user's net balance in cents (derived state):
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
    """A group of users with debt tracking for split payments."""

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
        self._expenses = [] # do stuff with this in the expense methods
        self.balances = {}
        if users is not None:
            self._add_users(*users)

    def __str__(self):
        return self.group_name

    def __repr__(self):
        return f"Group({self.group_name!r})"

    @property
    def group_id(self):
        return self._group_id

    @property
    def users(self):
        # enforce the invariant
        return tuple(self._users)

    @property
    def expenses(self):
        return tuple(self._expenses)

    def _add_users(self, *users):
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

    # TODO: write add_expense()
    # Should be the only way to add expenses (self._expenses), so:
        # payer belongs to this group
        # every debtor belongs to this group
    # TODO: write edit_expense()
    # TODO: write delete_expense()

    def _apply_expense(self, expense: Expense):
        if expense.split is not None:
            raise NotImplementedError() # only even splitting implemented for now
        share = expense.amount // (len(expense.debtors) + 1)
        remainder = expense.amount % (len(expense.debtors) + 1)
        if remainder == 0:
            for debtor in expense.debtors:
                self.balances[expense.payer][debtor] += share
                self.balances[debtor][expense.payer] -= share
        else:
            for i in range(remainder):
                self.balances[expense.payer][expense.debtors[i]] += share + 1
                self.balances[expense.debtors[i]][expense.payer] -= share + 1
            for j in range(remainder, len(expense.debtors)):
                self.balances[expense.payer][expense.debtors[j]] += share
                self.balances[expense.debtors[j]][expense.payer] -= share

class Expense:
    """
    A single expense within a group.
    This object is intended for direct use by Group instances only.
    """

    def __init__(
        self,
        payer: User,
        debtors: list[User],
        amount: int,
        description: str,
        split: dict[User, float] | None = None,
        expense_id: str | None = None,
    ):
        """
        This constructor is for use by a Group instance only. A new Expense
        should not be created using Expense(); instead, use App.add_expense().

        amount should be passed in as CENTS (int), not dollars (float).
        split should be passed in so that its:
        - keys include the payer and all debtors,
        - values represent the fraction of the amount each User is responsible for,
        - values sum to 1.
        If split is None, the amount is split equally.
        """
        self._expense_id = expense_id if expense_id is not None else str(uuid.uuid4())
        # immutable
        self._payer = payer # immutable
        self._created_at = datetime.now(timezone.utc) # immutable
        self._updated_at = datetime.now(timezone.utc) # to be modified by Group
        # validate
        self._debtors = debtors
        self._amount = amount
        self._description = description
        # TODO: later validate sum(split.values()) ==  1
        self._split = split

    # TODO: get rid of setter methods so that this object may eventually become
    # a frozen dataclass.
    # Group methods should be able to modify non-public attributes

    @property
    def expense_id(self):
        return self._expense_id

    @property
    def payer(self):
        return self._payer

    @property
    def debtors(self):
        return tuple(self._debtors)

    # @debtors.setter
    # def debtors(self, lst: list[User]):
    #     if not lst:
    #         raise ValueError("A split expense must have at least one debtor.")
    #     if self.payer in lst:
    #         raise ValueError("The payer cannot be a debtor of the same expense.")
    #     if len(lst) != len(set(lst)):
    #         raise ValueError("Debtors cannot contain duplicates.")
    #     self._debtors = lst

    @property
    def amount(self):
        return self._amount

    # @amount.setter
    # def amount(self, value: int):
    #     if not isinstance(value, int):
    #         raise ValueError("Amount must be an integer number of cents.")
    #     if value <= 0:
    #         raise ValueError("Amount must be positive.")
    #     self._amount = value

    @property
    def description(self):
        return self._description

    # @description.setter
    # def description(self, value: str):
    #     if not value.strip():
    #         raise ValueError("Description cannot be empty.")
    #     self._description = value.strip()

    @property
    def created_at(self):
        return self._created_at

    @property
    def split(self):
        return self._split
