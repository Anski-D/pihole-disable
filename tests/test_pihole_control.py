import os

import pytest
import pytest_responses  # noqa: F401
from responses import matchers

from pihole_disable.pihole_control import AuthManager, DnsPiholeManager

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


class TestDnsPiholeManager:
    def test_url_str(
        self, auth_manager: AuthManager, auth_headers: dict[str, str]
    ) -> None:
        dns_manager = DnsPiholeManager(auth_manager)

        assert dns_manager._url == API_URL + "/dns/blocking"

    @pytest.mark.parametrize("blocking, timer", [("disabled", 1), ("disabled", 999)])
    def test_check_blocking_disabled(
        self,
        blocking: str,
        timer: int | None,
        monkeypatch,
        auth_manager: AuthManager,
        auth_headers: dict[str, str],
        responses,
    ) -> None:
        monkeypatch.setattr(
            DnsPiholeManager,
            "check_blocking",
            DnsPiholeManager.check_blocking.__wrapped__,
        )
        dns_manager = DnsPiholeManager(auth_manager)
        responses.get(
            API_URL + "/dns/blocking",
            match=[
                matchers.header_matcher(auth_headers),
                matchers.json_params_matcher({}),
            ],
            json={"blocking": blocking, "timer": timer},
        )
        resp = dns_manager.check_blocking()

        assert all(
            [not resp["blocking"], isinstance(resp["timer"], int), resp["timer"] > 0]
        )

    def test_check_blocking_enabled(
        self,
        monkeypatch,
        auth_manager: AuthManager,
        auth_headers: dict[str, str],
        responses,
    ) -> None:
        monkeypatch.setattr(
            DnsPiholeManager,
            "check_blocking",
            DnsPiholeManager.check_blocking.__wrapped__,
        )
        dns_manager = DnsPiholeManager(auth_manager)
        responses.get(
            API_URL + "/dns/blocking",
            match=[
                matchers.header_matcher(auth_headers),
                matchers.json_params_matcher({}),
            ],
            json={"blocking": "enabled", "timer": None},
        )
        resp = dns_manager.check_blocking()

        assert resp["blocking"] and resp["timer"] == 0

    @pytest.mark.parametrize("timer", [4, 8, 16, 32, 64, 128])
    def test_disable_blocking(
        self,
        timer: int,
        monkeypatch,
        auth_manager: AuthManager,
        auth_headers: dict[str, str],
        responses,
    ) -> None:
        monkeypatch.setattr(
            DnsPiholeManager,
            "disable_blocking",
            DnsPiholeManager.disable_blocking.__wrapped__,
        )
        dns_manager = DnsPiholeManager(auth_manager)
        responses.post(
            API_URL + "/dns/blocking",
            match=[
                matchers.header_matcher(auth_headers),
                matchers.json_params_matcher({"blocking": False, "timer": 60 * timer}),
            ],
        )
        dns_manager.disable_blocking(timer)

    def test_enable_blocking(
        self,
        monkeypatch,
        auth_manager: AuthManager,
        auth_headers: dict[str, str],
        responses,
    ) -> None:
        monkeypatch.setattr(
            DnsPiholeManager,
            "enable_blocking",
            DnsPiholeManager.enable_blocking.__wrapped__,
        )
        dns_manager = DnsPiholeManager(auth_manager)
        responses.post(
            API_URL + "/dns/blocking",
            match=[
                matchers.header_matcher(auth_headers),
                matchers.json_params_matcher({"blocking": True}),
            ],
        )
        dns_manager.enable_blocking()
