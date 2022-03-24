import pytest
import os.path

from admin_bot.main import AdminBot


@pytest.fixture
def app():
    return AdminBot()


class TestApplication(object):
    def test_nothing(self):
        assert True

    def test_versioning(self, app):
        # App version must be present
        assert len(app.version) > 1
