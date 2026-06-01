import json
from functools import wraps
import logging
from typing import Protocol
from abc import ABC

import requests
import urllib3

log = logging.getLogger(__name__)
urllib3.disable_warnings()


def requires_auth(func):
    @wraps(func)
    def check_auth(obj: "Authable", *args, **kwargs):
        if not obj.auth_manager.is_authenticated:
            log.info("%s not authenticated", obj)
            obj.auth_manager.authenticate()

        return func(obj, *args, **kwargs)

    return check_auth


class AuthManager:
    _path = "/auth"

    def __init__(self, api_url: str, password: str) -> None:
        self.api_url = api_url
        self._password = password
        log.info("Created %s", self)
        self._url = self.api_url + self._path
        self._sid = ""
        self._csrf = ""
        self.authenticate()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.api_url}, {type(self._password)})"

    @property
    def headers(self) -> dict[str, str]:
        return {"X-FTL-SID": self._sid, "X-FTL-CSRF": self._csrf}

    @property
    def is_authenticated(self) -> bool:
        response = requests.request("GET", self._url, headers=self.headers, verify=False)

        return response.status_code == 200

    def authenticate(self) -> None:
        log.info("Authenticating %s with Pihole API", self)
        payload = {"password": self._password}
        response = json.loads(requests.request("POST", self._url, json=payload, verify=False).text)
        self._sid = response["session"]["sid"]
        self._csrf = response["session"]["csrf"]

    @requires_auth
    def logout(self) -> None:
        log.info("Logging out of Pihole API")
        requests.request("DELETE", self._url, headers=self.headers, verify=False)


class Authable(Protocol):
    auth_manager: AuthManager
    is_authenticated: bool

    def authenticate(self) -> None: ...


class PiholeManager(ABC):
    _path: str

    def __init__(self, auth_manager: AuthManager) -> None:
        self.auth_manager = auth_manager
        log.info("Created %s", self)
        self._url = self.auth_manager.api_url + self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.auth_manager})"


class DnsPiholeManager(PiholeManager):
    _path = "/dns/blocking"

    @requires_auth
    def check_blocking(self) -> dict[str, bool | int]:
        log.debug("Checking blocking status")

        response = json.loads(
            requests.request("GET", self._url, headers=self.auth_manager.headers, json={}, verify=False).text,
        )

        return {
            "blocking": response["blocking"] == "enabled",
            "timer": response["timer"] or 0,
        }

    @requires_auth
    def disable_blocking(self, period: float) -> None:
        log.info("Disabling blocking for %s minutes", round(period))
        payload = {
            "blocking": False,
            "timer": 60 * period, # Period in minutes converted to seconds
        }

        requests.request("POST", self._url, headers=self.auth_manager.headers, json=payload, verify=False)

    def increase_disable_period(self, period: float) -> None:
        current_status = self.check_blocking()
        log.info(
            "Increasing disable period from %s to %s minutes",
            round(current_status["timer"] / 60),
            round(current_status["timer"] / 60 + period),
        )
        self.disable_blocking(current_status["timer"] / 60 + period)

    @requires_auth
    def enable_blocking(self) -> None:
        log.info("Enabling blocking")
        payload = {
            "blocking": True,
        }

        requests.request("POST", self._url, headers=self.auth_manager.headers, json=payload, verify=False)


class ClientPiholeManager(PiholeManager):
    _path = "/info/client"

    def get_client_ip(self) -> dict[str, str]:
        response = json.loads(
            requests.request("GET", self._url, verify=False).text,
        )

        return {"IP": [_dict["value"] for _dict in response["headers"] if _dict["name"] == "X-Real-IP"][0]}


class GroupPiholeManager(PiholeManager):
    _path = "/groups"
    _group_name = "Disabled"

    @property
    def group_exists(self) -> bool:
        return self.get_group_id() > -1

    @requires_auth
    def get_group_id(self) -> int:
        response = json.loads(
            requests.request(
                "GET", self._url + "/" + self._group_name, headers=self.auth_manager.headers, verify=False,
            ).text,
        )

        if response["groups"]:
            return response["groups"][0]["id"]

        return -1

    @requires_auth
    def create_group(self) -> None:
        log.info("Creating group %s", self._group_name)
        if not self.group_exists:
            requests.request(
                "POST",
                self._url + "/" + self._group_name,
                headers=self.auth_manager.headers,
                verify=False,
            )

    @requires_auth
    def delete_group(self) -> None:
        log.info("Deleting group %s", self._group_name)
        requests.request(
            "DELETE",
            self._url + "/" + self._group_name,
            headers=self.auth_manager.headers,
            verify=False,
        )
