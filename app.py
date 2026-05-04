import os
import logging, logging.config

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request
import yaml

from pihole_disable.pihole_disable import PiholeDisabler

ENV_FILE = ".env"
LOGGING_CONFIG = "logging.yaml"
load_dotenv(ENV_FILE)
API_PASSWORD = os.environ["API_PASSWORD"]
disabler = PiholeDisabler(API_PASSWORD)


def _setup_logging() -> logging.Logger:
    with open(LOGGING_CONFIG) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    return logging.getLogger(__name__)


log = _setup_logging()


def create_app() -> Flask:
    log.info("Creating Flask app")

    return Flask(__name__)


app = create_app()


def _clean_period_value(period: float) -> float:
    return max(0, period)


@app.route("/")
def index():
    blocked = disabler.check_blocking()
    blocked["timer"] = round(blocked["timer"])

    return render_template(
        "index.html",
        blocked=blocked,
        refresh_period=5,
    )


@app.route("/enable")
def enable():
    disabler.enable_blocking()

    return redirect(url_for("index"))


@app.route("/disable", methods=("POST", "GET"))
@app.route("/disable/<period>")
def disable(period: str=""):
    if request.method == "POST":
        if (period := _clean_period_value(float(request.form["period"]))) > 0:
            disabler.disable_blocking(period)

        return redirect(url_for("index"))

    if period:
        disabler.increase_disable_period(_clean_period_value(int(period)))

        return redirect(url_for("index"))

    return render_template("disable.html", refresh_period=0)
