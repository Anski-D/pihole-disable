import json
from functools import wraps
import logging

import requests
import urllib3

URL_API = "https://pihole.dacyho.me/api"

log = logging.getLogger("__main__." + __name__)
urllib3.disable_warnings()


def requires_auth(func):
    @wraps(func)
    def check_auth(obj, *args, **kwargs):
        if not obj.is_authenticated:
            log.info("%s not authenticated", obj)
            obj.authenticate()

        return func(obj, *args, **kwargs)

    return check_auth


class PiholeDisabler:
    _auth_path = "/auth"
    _dns_path = "/dns/blocking"

    def __init__(self, password: str) -> None:
        self._password = password
        log.info("Created %s", self)
        self._sid = ""
        self._csrf = ""
        self.authenticate()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({type(self._password).__name__})"

    @property
    def headers(self) -> dict[str, str]:
        return {"X-FTL-SID": self._sid, "X-FTL-CSRF": self._csrf}

    @property
    def is_authenticated(self) -> bool:
        url = f"{URL_API}{self._auth_path}"
        response = requests.request("GET", url, headers=self.headers, verify=False)

        return response.status_code == 200

    def authenticate(self) -> None:
        log.info("Authenticating %s with Pihole API", self)
        url = f"{URL_API}{self._auth_path}"
        payload = {"password": self._password}
        response = json.loads(requests.request("POST", url, json=payload, verify=False).text)
        self._sid = response["session"]["sid"]
        self._csrf = response["session"]["csrf"]

    @requires_auth
    def check_blocking(self) -> dict[str, bool | int]:
        log.debug("Checking blocking status")
        url = f"{URL_API}{self._dns_path}"

        response = json.loads(requests.request("GET", url, headers=self.headers, json={}, verify=False).text)

        return {
            "blocking": response["blocking"] == "enabled",
            "timer": response["timer"] or 0,
        }

    @requires_auth
    def disable_blocking(self, period: float) -> None:
        log.info("Disabling blocking for %s minutes", round(period))
        url = f"{URL_API}{self._dns_path}"
        payload = {
            "blocking": False,
            "timer": 60 * period, # Period in minutes converted to seconds
        }

        requests.request("POST", url, headers=self.headers, json=payload, verify=False)

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
        url = f"{URL_API}{self._dns_path}"
        payload = {
            "blocking": True,
        }

        requests.request("POST", url, headers=self.headers, json=payload, verify=False)

    @requires_auth
    def logout(self) -> None:
        log.info("Logging out of Pihole API")
        url = f"{URL_API}{self._auth_path}"

        requests.request("DELETE", url, headers=self.headers, verify=False)
