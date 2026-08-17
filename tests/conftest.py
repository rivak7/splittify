import pytest

from splittify.app import App

@pytest.fixture
def app():
    return App()
