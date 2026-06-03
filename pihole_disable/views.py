from flask import render_template, redirect, url_for, request

from pihole_disable import app, API_URL, API_PASSWORD
from pihole_disable.pihole_disable import (
    AuthManager,
    PiholeController,
    ClientPiholeManager,
)

auth_manager = AuthManager(API_URL, API_PASSWORD)
pihole_controller = PiholeController(auth_manager)
dns_manager = pihole_controller.dns_manager


def _clean_period_value(period: float) -> float:
    return max(0, period)


@app.route("/")
def index():
    blocked = dns_manager.check_blocking()
    blocked["timer"] = round(blocked["timer"])

    return render_template(
        "index.html",
        blocked=blocked,
        refresh_period=5,
    )


@app.route("/enable")
def enable():
    dns_manager.enable_blocking()

    return redirect(url_for("index"))


@app.route("/disable", methods=("POST", "GET"))
@app.route("/disable/<period>")
def disable(period: str=""):
    if request.method == "POST":
        if (period := _clean_period_value(float(request.form["period"]))) > 0:
            dns_manager.disable_blocking(period)

        return redirect(url_for("index"))

    if period:
        dns_manager.increase_disable_period(_clean_period_value(int(period)))

        return redirect(url_for("index"))

    return render_template("disable.html", refresh_period=0)


@app.route("/status")
def status() -> dict:
    return dns_manager.check_blocking()


@app.route("/client")
def client() -> dict[str, str]:
    return ClientPiholeManager.get_client_ip(API_URL)
