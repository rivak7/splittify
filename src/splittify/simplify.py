"""Turn net balances into a short list of payments needed to settle a group."""
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:   # type hints only, avoids a circular import with models.py
    from .models import User


class Payment(NamedTuple):
    debtor: User
    creditor: User
    amount: int


def _check_balanced(nets: dict[User, int]) -> None:
    """Raise ValueError unless the nets sum to zero."""
    total = sum(nets.values())
    if total != 0:
        raise ValueError(
            f"All debts in a group must cancel! Got total: {total}"
        )


def greedy_simplify(nets: dict[User, int]) -> list[Payment]:
    """
    Settle everyone in at most n-1 payments. NOT guaranteed minimal.

    nets: user -> net balance in cents (positive = owed money). Must sum to 0.
    Does not modify its input.

    The algorithm greedily matches the debtor with the highest absolute net to
    the creditor with the highest net. Ties are broken by user_id, so output
    is deterministic.
    """
    _check_balanced(nets)

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


def exact_simplify(nets: dict[User, int]) -> list[Payment]:
    """
    Settle everyone in the minimum possible number of payments.

    nets: user -> net balance in cents (positive = owed money). Must sum to 0.
    Does not modify its input.

    With n users whose net is non-zero, a group can always be settled in n-1
    payments, and every subgroup whose nets already sum to zero saves one more.
    So this splits the users into the largest possible number k of disjoint
    zero-sum subgroups (a bitmask DP over subsets), settles each one with
    greedy_simplify, and returns the n-k payments concatenated. Users are
    ordered by user_id, so output is deterministic.

    Runs in O(2^n * n) time and O(2^n) memory, so it is only practical for
    small groups (about 20 non-zero users takes a second or two).
    """
    _check_balanced(nets)

    # users with a zero net never pay or get paid; sort so output is
    # deterministic
    users = sorted(
        (u for u, net in nets.items() if net != 0), key=lambda u: u.user_id
    )
    n = len(users)
    full = (1 << n) - 1

    # sums[mask]: total net of the users in mask
    sums = [0] * (1 << n)
    for mask in range(1, full + 1):
        low = mask & -mask
        sums[mask] = sums[mask ^ low] + nets[users[low.bit_length() - 1]]

    # dp[mask]: max number of zero-sum masks on a path that removes one user at
    # a time from mask down to 0. When sums[mask] == 0, this is the max number
    # of disjoint zero-sum subgroups that mask can be split into.
    dp = [0] * (1 << n)
    for mask in range(1, full + 1):
        best = max(dp[mask ^ (1 << i)] for i in range(n) if mask >> i & 1)
        dp[mask] = best + (sums[mask] == 0)

    # walk back down the best path; each stretch between consecutive zero-sum
    # masks is one subgroup, settled on its own in (size - 1) payments
    payments: list[Payment] = []
    mask = group_start = full
    while mask:
        # remove a user whose removal leads to a mask that achieves dp[mask];
        # taking the lowest such index keeps the output deterministic
        target = dp[mask] - (sums[mask] == 0)
        for i in range(n):
            bit = 1 << i
            if mask & bit and dp[mask ^ bit] == target:
                break
        mask ^= bit
        if sums[mask] == 0:
            group = group_start ^ mask
            payments += greedy_simplify(
                {users[j]: nets[users[j]] for j in range(n) if group >> j & 1}
            )
            group_start = mask

    return payments
