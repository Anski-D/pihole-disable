import os
import json
import argparse
from functools import wraps

import requests
from dotenv import load_dotenv

ENV_FILE = ".env"
URL_API = "https://pihole.dacyho.me/api"
STOP_FILE = "STOP"
SHUTDOWN_CHECK_PERIOD = 10
DEBUG = False

load_dotenv(ENV_FILE)
API_PASSWORD = os.environ["API_PASSWORD"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="port to listen on")
    parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")

    return parser.parse_args()


def requires_auth(func):
    @wraps(func)
    def check_auth(obj, *args, **kwargs):
        if not obj.is_authenticated:
            obj.authenticate()

        return func(obj, *args, **kwargs)

    return check_auth


class PiholeDisabler:
    _sid: str = ""
    _csrf: str = ""
    _auth_path = "/auth"
    _dns_path = "/dns/blocking"

    def __init__(self, password: str) -> None:
        self._password = password
        self.authenticate()

    @property
    def headers(self) -> dict[str, str]:
        return {"X-FTL-SID": self._sid, "X-FTL-CSRF": self._csrf}

    @property
    def is_authenticated(self) -> bool:
        url = f"{URL_API}{self._auth_path}"
        response = requests.request("GET", url, headers=self.headers, verify=False)

        return response.status_code == 200

    def authenticate(self) -> None:
        url = f"{URL_API}{self._auth_path}"
        payload = {"password": self._password}
        response = json.loads(requests.request("POST", url, json=payload, verify=False).text)
        self._sid = response["session"]["sid"]
        self._csrf = response["session"]["csrf"]

    @requires_auth
    def check_blocking(self) -> dict[str, bool | int]:
        url = f"{URL_API}{self._dns_path}"

        response = json.loads(requests.request("GET", url, headers=self.headers, json={}, verify=False).text)

        return {
            "blocking": response["blocking"] == "enabled",
            "timer": response["timer"] or 0,
        }

    @requires_auth
    def disable_blocking(self, period: float) -> None:
        url = f"{URL_API}{self._dns_path}"
        payload = {
            "blocking": False,
            "timer": 60 * period, # Period in minutes
        }

        requests.request("POST", url, headers=self.headers, json=payload, verify=False)

    def increase_disable_period(self, period: float) -> None:
        current_status = self.check_blocking()
        self.disable_blocking(current_status["timer"]/60 + period)

    @requires_auth
    def enable_blocking(self) -> None:
        url = f"{URL_API}{self._dns_path}"
        payload = {
            "blocking": True,
        }

        requests.request("POST", url, headers=self.headers, json=payload, verify=False)

    @requires_auth
    def logout(self) -> None:
        url = f"{URL_API}{self._auth_path}"

        requests.request("DELETE", url, headers=self.headers, verify=False)
