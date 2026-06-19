import os

import pytest

from pihole_disable.pihole_control import AuthManager

API_URL = os.environ["API_URL"]
API_PASSWORD = os.environ["API_PASSWORD"]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-FTL-SID": "dummy_sid",
        "X-FTL-CSRF": "dummy_csrf",
    }


@pytest.fixture
def auth_manager(monkeypatch, auth_headers: dict[str, str]) -> AuthManager:
    monkeypatch.setattr(AuthManager, "is_authenticated", lambda _: True)
    monkeypatch.setattr(AuthManager, "authenticate", lambda _: None)

    auth_manager = AuthManager(API_URL, API_PASSWORD)
    auth_manager._sid = auth_headers["X-FTL-SID"]
    auth_manager._csrf = auth_headers["X-FTL-CSRF"]

    return auth_manager


class TestAuthManager:
    def test_url_str(self, auth_manager):
        assert auth_manager._url == API_URL + "/auth"
