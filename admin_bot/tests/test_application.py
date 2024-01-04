import pytest
import os.path
import discord

from admin_bot.main import AdminBot

from admin_bot.utilities.yamlTools import getSuggestion


@pytest.fixture
def app():
    return AdminBot()


class TestApplication(object):
    def test_nothing(self):
        assert True

    def test_versioning(self, app):
        # App version must be present
        assert len(app.version) > 1

    def test_suggestions(self):
        assert len(getSuggestion(["@everyone"]))
