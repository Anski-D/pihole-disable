import json
from functools import wraps
import logging
from typing import Protocol
from abc import ABC
import asyncio
import time

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


class GroupPiholeManager(PiholeManager):
    _path = "/groups"
    _group_name = "Disabled"

    def __init__(self, auth_manager: AuthManager) -> None:
        super().__init__(auth_manager)

        self.delete_group()
        self.create_group()

    @property
    def group_exists(self) -> bool:
        log.debug("Checking if group %s exists", self._group_name)
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
        if not self.group_exists:
            log.info("Creating group %s", self._group_name)
            requests.request(
                "PUT",
                self._url + "/" + self._group_name,
                headers=self.auth_manager.headers,
                json={},
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


class ClientPiholeManager(PiholeManager):
    _path = "/clients"

    def __init__(self, auth_manager: AuthManager, group_manager: GroupPiholeManager, client: str) -> None:
        super().__init__(auth_manager)
        self._group_manager = group_manager
        self._client = client

    @property
    def client(self) -> str:
        return self._client

    @classmethod
    def get_client_ip(cls, api_url: str) -> dict[str, str]:
        response = json.loads(
            requests.request("GET", api_url + "/info/client", verify=False).text,
        )

        return {"IP": [_dict["value"] for _dict in response["headers"] if _dict["name"] == "X-Real-IP"][0]}

    @property
    @requires_auth
    def client_exists(self) -> bool:
        response = json.loads(
            requests.request("GET", self._url + "/" + self._client, headers=self.auth_manager.headers, verify=False).text,
        )

        return bool(response["clients"])

    @requires_auth
    def move_client_to_group(self) -> None:
        self._group_manager.create_group()
        payload = {"groups": [self._group_manager.get_group_id()]}

        requests.request("PUT", self._url + "/" + self._client, headers=self.auth_manager.headers, json=payload, verify=False)

    @requires_auth
    def delete_client(self) -> None:
        requests.request("DELETE", self._url + "/" + self._client, headers=self.auth_manager.headers, verify=False)


class DisabledClient:
    _sleep: asyncio.Task

    def __init__(self, client_manager: ClientPiholeManager) -> None:
        self._client_manager = client_manager
        log.debug("Creating %s", self)

        self._time_start = time.monotonic()
        self._period = 0

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._client_manager})"

    @property
    def client(self) -> str:
        return self._client_manager.client

    async def client_disable_pihole(self, period: float) -> None:
        self._period = period  # In seconds
        log.debug("Removing %s from Pihole blocking for %s seconds", self.client, self._period)
        self._time_start = time.monotonic()
        self._client_manager.move_client_to_group()
        self._sleep = asyncio.create_task(asyncio.sleep(self._period))
        await self._sleep
        log.debug("Reactivating blocking for %s", self.client)
        self._client_manager.delete_client()

    def cancel_sleep(self) -> None:
        log.debug("Canceling sleep for %s, %s seconds were left", self.client, self.query_remaining_period())
        self._sleep.cancel()

    def query_remaining_period(self) -> int:
        return max(0, round(self._period - (time.monotonic() - self._time_start)))

    
class PiholeController:
    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager
        log.info("Creating %s", self)
        
        self._dns_manager = DnsPiholeManager(auth_manager)
        self._group_manager = GroupPiholeManager(auth_manager)
        
        self._disabled_clients: dict[str, DisabledClient] = {}
        
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._auth_manager})"
    
    @property
    def dns_manager(self) -> DnsPiholeManager:
        return self._dns_manager
    
    async def disable_client(self, client: str, period: float) -> None:
        disabled_client = self._disabled_clients.get(client)
        if disabled_client is None:
            disabled_client = DisabledClient(ClientPiholeManager(self._auth_manager, self._group_manager, client))
            self._disabled_clients[client] = disabled_client
        else:
            disabled_client.cancel_sleep()

        if period > 0:
            await disabled_client.client_disable_pihole(60 * period)

        del self._disabled_clients[client]
