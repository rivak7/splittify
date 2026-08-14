"""Unit tests for the application state and entity registries in Splittify."""

import pytest

from splittify.app import App
from splittify.models import User, Group


@pytest.fixture
def app():
    return App()


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
    group.add_users(alice)

    assert len(group.users) == 1
    assert alice in group.users

    assert len(alice.groups) == 1
    assert group in alice.groups


def test_group_initializes_complete_zero_balance_graph(app):
    alice = app.new_user("Alice")
    bob = app.new_user("Bob")
    charlie = app.new_user("Charlie")
    group = app.new_group("Trip", [alice, bob, charlie])

    edges = 0
    for user_edges in group.balances.values():
        for balance in user_edges.values():
            assert balance == 0
            edges += 1
    assert edges == len(group.users) * (len(group.users) - 1)


def test_app_returns_canonical_registered_user(app):
    alice = app.new_user("Alice")
    user = app.find_user(alice.user_id)
    assert user is alice


def test_app_returns_canonical_registered_group(app):
    alice = app.new_user("Alice")
    bob = app.new_user("Bob")
    trip = app.new_group("Trip", [alice, bob])
    group = app.find_group(trip.group_id)
    assert group is trip


def test_new_group_rejects_unregistered_user(app):
    real_alice = app.new_user("Alice")
    imposter_alice = User("Alice", user_id=real_alice.user_id)

    with pytest.raises(ValueError):
        app.new_group("Trip", [imposter_alice])
