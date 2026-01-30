import os
from typing import Any
import json
import argparse

import requests
from dotenv import load_dotenv
import tornado.web

ENV_FILE = ".env"
URL_API = "https://pihole.dacyho.me/api"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "period",
        nargs="?",
        type=int,
        default=1,
        help="how many minutes to disable Pihole",
    )

    return parser.parse_args()


class PiholeDisabler:
    _sid: str
    _csrf: str
    _auth_path = "/auth"
    _dns_path = "/dns/blocking"

    def __init__(self, password: str) -> None:
        self._password = password
        self.authenticate()

    def authenticate(self) -> None:
        url = f"{URL_API}{self._auth_path}"
        payload = {"password": self._password}

        response =  json.loads(requests.request("POST", url, json=payload, verify=False).text)
        self._sid = response["session"]["sid"]
        self._csrf = response["session"]["csrf"]

    def disable_blocking(self, period: int) -> dict[str, Any]:
        url = f"{URL_API}{self._dns_path}"
        headers = {
            "X-FTL-SID": self._sid,
            "X-FTL-CSRF": self._csrf,
        }
        payload = {
            "blocking": False,
            "timer": 60 * period, # Period in minutes
        }

        return json.loads(requests.request("POST", url, headers=headers, json=payload, verify=False).text)

    def logout(self) -> None:
        url = f"{URL_API}{self._auth_path}"
        headers = {
            "X-FTL-SID": self._sid,
            "X-FTL-CSRF": self._csrf,
        }
        payload = {}

        requests.request("DELETE", url, headers=headers, data=payload, verify=False)


def main():
    args = parse_args()
    load_dotenv(ENV_FILE)

    disabler = PiholeDisabler(os.getenv("API_PASSWORD"))
    disabler.disable_blocking(args.period)
    disabler.logout()
