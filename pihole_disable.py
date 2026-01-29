import os
from typing import Any
import json
import argparse

import requests
from dotenv import load_dotenv

URL_API = "https://pihole.dacyho.me/api"
AUTH_PATH = "/auth"
DNS_PATH = "/dns/blocking"


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


def authenticate(_api_pass: str) -> dict[str, Any]:
    url = f"{URL_API}{AUTH_PATH}"
    payload = {"password": _api_pass}

    return json.loads(requests.request("POST", url, json=payload, verify=False).text)


def disable_blocking(_sid: str, period: int) -> dict[str, Any]:
    url = f"{URL_API}{DNS_PATH}"
    payload = {
        "sid": _sid,
        "blocking": False,
        "timer": 60 * period, # Period in minutes
    }

    return json.loads(requests.request("POST", url, json=payload, verify=False).text)


def logout(_sid: str) -> None:
    url = f"{URL_API}{AUTH_PATH}"
    payload = {"sid": _sid}

    requests.request("DELETE", url, data=payload, verify=False)


if __name__ == "__main__":
    args = parse_args()
    load_dotenv(".env")
    api_pass = os.environ.get("API_PASS")

    response = authenticate(api_pass)
    sid = response["session"]["sid"]

    disable_blocking(sid, args.period)

    logout(sid)
