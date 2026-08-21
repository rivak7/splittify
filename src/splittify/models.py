"""Models for Users and Groups of Users in Splittify App instances."""

from __future__ import annotations
from types import MappingProxyType
from datetime import datetime, timezone
import math
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

    def _add_expense(
        self,
        payer: User,
        debtors: list[User],
        amount: int,
        description: str,
        split: dict[User, float] | None = None,
        expense_id: str | None = None,
    ) -> Expense:
        expense_mismatch_error = ValueError(
            "Expense mismatches Group: "
            "not all Users involved in the Expense are members of this Group."
        )
        if payer not in self._users:
            raise expense_mismatch_error
        for debtor in debtors:
            if debtor not in self._users:
                raise expense_mismatch_error

        expense = Expense(
            payer,
            debtors,
            amount,
            description,
            split,
            expense_id,
        )

        self._apply_expense(expense)
        self._expenses.append(expense)
        return expense

    # TODO: write edit_expense()
    # TODO: write delete_expense()

    def _apply_expense(self, expense: Expense, remove=False):
        """
        Logic for updating the balance graph after a shared expense.

        For evenly split expenses (expense.split is None):
            base_share is calculated as floor(amount/n) where n is the number of
            users involved in the shared expense.
            There is a remainder r = amount mod n. When r is nonzero, one extra
            cent is assigned to the debts of each of the first r debtors.
            The payer never pays an 'extra' cent.
        """
        if expense.split is not None:
            raise NotImplementedError("Only even splitting implemented for now.")

        mult = -1 if remove else 1
        base_share = (expense.amount // (len(expense.debtors) + 1)) * mult
        remainder = expense.amount % (len(expense.debtors) + 1)

        for i, debtor in enumerate(expense.debtors):
            share = base_share + mult if i < remainder else base_share
            self.balances[expense.payer][debtor] += share
            self.balances[debtor][expense.payer] -= share


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
        # validate first
        if not debtors:
            raise ValueError("A split expense must have at least one debtor.")
        if payer in debtors:
            raise ValueError("The payer cannot be a debtor of the same expense.")
        if len(debtors) != len(set(debtors)):
            raise ValueError("Debtors cannot contain duplicates.")

        if not isinstance(amount, int):
            raise ValueError("Amount must be an integer number of cents.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        if not description.strip():
            raise ValueError("Description cannot be empty.")

        if split is not None:
            if not(math.isclose(sum(split.values()), 1)):
                raise ValueError("Invalid split: values must sum to 1.")

        self._expense_id = (
            expense_id if expense_id is not None
            else str(uuid.uuid4())
        )
        self._payer = payer
        self._created_at = datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc) # to be modified by Group
        self._debtors = tuple(debtors)
        self._amount = amount
        self._description = description.strip()
        self._split = split.copy() if split is not None else None

    # Group methods will directly modify non-public attributes

    @property
    def expense_id(self):
        return self._expense_id

    @property
    def payer(self):
        return self._payer

    @property
    def debtors(self):
        return self._debtors

    @property
    def amount(self):
        return self._amount

    @property
    def description(self):
        return self._description

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def split(self):
        # return a read-only view of the dictionary
        # can use frozendict() in Python 3.15+,
        # but the version was not yet stable at the time of writing
        return MappingProxyType(self._split) if self._split is not None else None
