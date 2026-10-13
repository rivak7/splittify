"""Turn net balances into a short list of payments needed to settle a group."""
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:   # type hints only, avoids a circular import with models.py
    from .models import User


class Payment(NamedTuple):
    debtor: User
    creditor: User
    amount: int


def greedy_simplify(nets: dict[User, int]) -> list[Payment]:
    """
    Settle everyone in at most n-1 payments. NOT guaranteed minimal.

    nets: user -> net balance in cents (positive = owed money). Must sum to 0.
    Does not modify its input.

    The algorithm greedily matches the debtor with the highest absolute net to
    the creditor with the highest net. Ties are broken by user_id, so output
    is deterministic.
    """
    total = sum(nets.values())
    if total != 0:
        raise ValueError(
            f"All debts in a group must cancel! Got total: {total}"
        )

    creditors: dict[User, int] = {}
    debtors: dict[User, int] = {}
    payments: list[Payment] = []

    for user, net in nets.items():
        if net > 0:
            creditors[user] = net
        elif net < 0:
            debtors[user] = -net

    while debtors:
        debtor = max(debtors, key=lambda u: (debtors[u], u.user_id))
        creditor = max(creditors, key=lambda u: (creditors[u], u.user_id))
        amount = min(debtors[debtor], creditors[creditor])
        payment = Payment(debtor, creditor, amount)
        payments.append(payment)
        debtors[debtor] -= amount
        creditors[creditor] -= amount
        if debtors[debtor] == 0:
            del debtors[debtor]
        if creditors[creditor] == 0:
            del creditors[creditor]

    return payments
