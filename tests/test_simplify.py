"""Unit tests for debt simplification in Splittify."""

import random

import pytest

from splittify.models import User
from splittify.simplify import Payment, greedy_simplify


def settle(nets, payments):
    """Return the net balances left after making every payment."""
    remaining = dict(nets)
    for payment in payments:
        remaining[payment.debtor] += payment.amount
        remaining[payment.creditor] -= payment.amount
    return remaining


@pytest.fixture
def users():
    # fixed user_ids so tie-breaking is predictable
    return [User(name, user_id=name.lower()) for name in "ABCDE"]


def test_largest_debtor_pays_largest_creditor_first(users):
    a, b, c, d = users[:4]
    nets = {a: 70, b: 30, c: -60, d: -40}

    assert greedy_simplify(nets) == [
        Payment(c, a, 60),
        Payment(d, b, 30),
        Payment(d, a, 10),
    ]


def test_ties_are_broken_by_user_id(users):
    a, b, c = users[:3]
    # a and b are owed the same amount; the larger user_id ("b") is paid first
    assert greedy_simplify({a: 50, b: 50, c: -100}) == [
        Payment(c, b, 50),
        Payment(c, a, 50),
    ]


def test_random_groups_settle_in_at_most_n_minus_one_payments():
    rng = random.Random(42)
    for _ in range(200):
        n = rng.randint(2, 8)
        group = [User(f"U{i}", user_id=f"u{i}") for i in range(n)]
        amounts = [rng.randint(-10_000, 10_000) for _ in range(n - 1)]
        amounts.append(-sum(amounts))
        nets = dict(zip(group, amounts))

        payments = greedy_simplify(nets)

        assert all(value == 0 for value in settle(nets, payments).values())
        assert len(payments) <= n - 1
        for payment in payments:
            assert isinstance(payment.amount, int)
            assert payment.amount > 0
            assert nets[payment.debtor] < 0 < nets[payment.creditor]
