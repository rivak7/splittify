"""Unit tests for the Group state and expense logic in Splittify."""

from types import SimpleNamespace

import pytest

from splittify.app import App


@pytest.fixture
def trip(app):
    alice = app.new_user("Alice")
    bob = app.new_user("Bob")
    charlie = app.new_user("Charlie")
    group = app.new_group("Trip", [alice, bob, charlie])

    return SimpleNamespace(
        app=app,
        alice=alice,
        bob=bob,
        charlie=charlie,
        group=group,
    )


def test_group_membership_is_bidirectional(app):
    alice = app.new_user("Alice")
    bob = app.new_user("Bob")
    group = app.new_group("Trip", [alice, bob])

    assert alice in group.users
    assert bob in group.users
    assert group in alice.groups
    assert group in bob.groups


def test_duplicate_user_addition_does_not_change_membership(app):
    alice = app.new_user("Alice")
    group = app.new_group("Trip", [alice])
    app.add_users_to_group(group, alice)

    assert len(group.users) == 1
    assert alice in group.users

    assert len(alice.groups) == 1
    assert group in alice.groups


def test_group_initializes_complete_zero_balance_graph(trip):
    edges = 0
    for user_edges in trip.group.balances.values():
        for balance in user_edges.values():
            assert balance == 0
            edges += 1

    assert edges == len(trip.group.users) * (len(trip.group.users) - 1)


def test_expense_of_sixty_dollars_splits_evenly_among_three(trip):
    trip.app.add_expense(
        trip.group,
        trip.alice,
        [trip.bob, trip.charlie],
        6000,
        "tickets",
    )

    assert trip.alice.net_balance() == 4000
    assert trip.bob.net_balance() == -2000

    assert trip.group.balances[trip.alice][trip.bob] == 2000
    assert trip.group.balances[trip.charlie][trip.alice] == -2000
    assert trip.group.balances[trip.bob][trip.charlie] == 0


def test_expense_of_one_dollar_among_three_gives_extra_cent_to_first_debtor(trip):
    trip.app.add_expense(
        trip.group,
        trip.alice,
        [trip.bob, trip.charlie],
        100,
        "candy",
    )

    assert trip.alice.net_balance() == 67
    assert trip.bob.net_balance() == -34
    assert trip.charlie.net_balance() == -33


def test_expenses_accumulate_correctly(trip):
    trip.app.add_expense(
        trip.group,
        trip.alice,
        [trip.bob, trip.charlie],
        6000,
        "tickets",
    )
    trip.app.add_expense(
        trip.group,
        trip.bob,
        [trip.alice],
        75,
        "candy",
    )

    assert trip.alice.net_balance() == 4000 - 38
    assert trip.bob.net_balance() == -2000 + 38
    assert trip.charlie.net_balance() == -2000
    assert (
        trip.group.balances[trip.alice][trip.bob]
        == -trip.group.balances[trip.bob][trip.alice]
    )


def test_deleting_expense_restores_group_state(trip):
    expense = trip.app.add_expense(
        trip.group,
        trip.alice,
        [trip.bob, trip.charlie],
        100,
        "candy",
    )
    deleted_expense = trip.app.delete_expense(
        trip.group,
        expense.expense_id,
    )

    assert deleted_expense is expense
    assert expense not in trip.group.expenses

    for user_balances in trip.group.balances.values():
        for balance in user_balances.values():
            assert balance == 0


def test_deleting_many_expenses_with_leftover_cents_restores_zero_balances(trip):
    expenses = [
        # 100 % 3 == 1 leftover cent
        trip.app.add_expense(
            trip.group, trip.alice, [trip.bob, trip.charlie], 100, "candy"
        ),
        # 1001 % 3 == 2 leftover cents
        trip.app.add_expense(
            trip.group, trip.bob, [trip.alice, trip.charlie], 1001, "dinner"
        ),
        # 7 % 2 == 1 leftover cent
        trip.app.add_expense(
            trip.group, trip.charlie, [trip.alice], 7, "gum"
        ),
        # 6000 % 3 == 0 leftover cents
        trip.app.add_expense(
            trip.group, trip.alice, [trip.bob, trip.charlie], 6000, "hotel"
        ),
    ]

    assert any(
        balance != 0
        for user_balances in trip.group.balances.values()
        for balance in user_balances.values()
    )

    # delete out of creation order
    for i in (2, 0, 3, 1):
        trip.app.delete_expense(trip.group, expenses[i].expense_id)

    assert trip.group.expenses == ()
    for user_balances in trip.group.balances.values():
        for balance in user_balances.values():
            assert balance == 0
    for user in trip.group.users:
        assert user.net_balance(trip.group) == 0


def test_simplify_debts_settles_group_without_changing_balances(trip):
    trip.app.add_expense(
        trip.group,
        trip.alice,
        [trip.bob, trip.charlie],
        6000,
        "tickets",
    )
    trip.app.add_expense(
        trip.group,
        trip.bob,
        [trip.alice, trip.charlie],
        10001,
        "dinner",
    )
    balances_before = {
        user: dict(user_balances)
        for user, user_balances in trip.group.balances.items()
    }
    nets = {user: user.net_balance(trip.group) for user in trip.group.users}

    payments = trip.group.simplify_debts()

    assert trip.group.balances == balances_before
    for payment in payments:
        nets[payment.debtor] += payment.amount
        nets[payment.creditor] -= payment.amount
    assert all(net == 0 for net in nets.values())
