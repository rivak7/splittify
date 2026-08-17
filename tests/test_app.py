"""Unit tests for the app entity registries in Splittify."""

import pytest

from splittify.app import App
from splittify.models import User


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
