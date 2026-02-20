import os
import json
import argparse
import asyncio
from pathlib import Path
from functools import wraps

import requests
from dotenv import load_dotenv
import tornado.web, tornado.gen
import urllib3

urllib3.disable_warnings()

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
    def check_auth(self, *args, **kwargs):
        url = f"{URL_API}{self._auth_path}"
        response = requests.request("GET", url, headers=self.headers, verify=False)

        if response.status_code != 200:
            self.authenticate()

        return func(self, *args, **kwargs)

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


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, _disabler: PiholeDisabler) -> None:
        self._disabler = _disabler

    def get(self, command: str | None = None) -> None:
        template = "templates/index.html"
        refresh_period = 5
        command = command.lower()
        match command:
            case "enable":
                self._disabler.enable_blocking()
            case "disable":
                template = "templates/disable.html"
                refresh_period = 0

        self.render(
            template,
            blocked=self._disabler.check_blocking(),
            refresh_period=refresh_period,
        )

    def post(self, command: str) -> None:
        if command.lower() == "disable" and (period := _clean_period_value(float(self.get_argument("period")))) > 0:
            self._disabler.disable_blocking(period)

        self.redirect("/")


def _clean_period_value(period: float) -> float:
    return max(0, period)


def make_app(_disabler: PiholeDisabler) -> tornado.web.Application:
    return tornado.web.Application(
        [
            (r"/(.*)", MainHandler, dict(_disabler=_disabler)),
        ],
        debug=DEBUG,
        static_path="static",
    )


async def main(port:int, _disabler: PiholeDisabler) -> None:
    app = make_app(_disabler)
    app.listen(port)

    await check_shutdown()


async def check_shutdown() -> None:
    while not (stop_file := Path(STOP_FILE)).exists():
        await tornado.gen.sleep(SHUTDOWN_CHECK_PERIOD)

    stop_file.unlink(missing_ok=True)


if __name__ == "__main__":
    args = parse_args()
    DEBUG = args.debug
    disabler = PiholeDisabler(API_PASSWORD)

    try:
        asyncio.run(main(args.port, disabler))
    except KeyboardInterrupt:
        disabler.logout()
    else:
        disabler.logout()
