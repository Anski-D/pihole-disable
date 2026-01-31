import os
from typing import Any
import json
import argparse
import asyncio

import requests
from dotenv import load_dotenv
import tornado.web

ENV_FILE = ".env"
URL_API = "https://pihole.dacyho.me/api"
API_PASSWORD = ""

load_dotenv(ENV_FILE)


def _load_password() -> str:
    if not (_pass := os.environ.get("API_PASSWORD")):
        raise KeyError("API password not set")

    return _pass


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

    def authenticate(self) -> None:
        if not self._is_authenticated():
            url = f"{URL_API}{self._auth_path}"
            payload = {"password": self._password}

            response =  json.loads(requests.request("POST", url, json=payload, verify=False).text)
            self._sid = response["session"]["sid"]
            self._csrf = response["session"]["csrf"]

    def check_blocking(self) -> dict[str, bool | int]:
        self.authenticate()
        url = f"{URL_API}{self._dns_path}"

        response = json.loads(requests.request("GET", url, headers=self.headers, json={}, verify=False).text)

        return {
            "blocking": response["blocking"] == "enabled",
            "timer": response["timer"] or 0,
        }

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
        if self._is_authenticated():
            url = f"{URL_API}{self._auth_path}"

            requests.request("DELETE", url, headers=self.headers, verify=False)

    def _is_authenticated(self) -> bool:
        url = f"{URL_API}{self._auth_path}"

        response = requests.request("GET", url, headers=self.headers, verify=False)

        return response.status_code != 401 and response.status_code == 200


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, _disabler: PiholeDisabler) -> None:
        self._disabler = _disabler

    def get(self):
        self.render(
            "templates/index.html",
            blocked=self._disabler.check_blocking(),
            refresh_period=5,
        )


class InputHandler(tornado.web.RequestHandler):
    def initialize(self, _disabler: PiholeDisabler) -> None:
        self._disabler = _disabler

    def get(self) -> None:
        self.render(
            "templates/disable.html",
            refresh_period=0,
        )

    def post(self):
        if period := _clean_period_value(float(self.get_argument("period"))) > 0:
            self._disabler.disable_blocking(period)

        self.redirect("/")


def _clean_period_value(period: float) -> float:
    return max(0, period)


def make_app(_disabler: PiholeDisabler) -> tornado.web.Application:
    return tornado.web.Application(
        [
            (r"/", MainHandler, dict(_disabler=_disabler)),
            (r"/disable", InputHandler, dict(_disabler=_disabler)),
        ],
        debug=True,
    )


async def main(_disabler: PiholeDisabler) -> None:
    app = make_app(_disabler)
    app.listen(8888)
    shutdown_event = asyncio.Event()

    await shutdown_event.wait()


if __name__ == "__main__":
    API_PASSWORD = _load_password()
    disabler = PiholeDisabler(API_PASSWORD)

    try:
        asyncio.run(main(disabler))
    except KeyboardInterrupt:
        disabler.logout()
