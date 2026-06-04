from quart import render_template, redirect, url_for, request

from pihole_disable import app, API_URL, API_PASSWORD
from pihole_disable.pihole_control import (
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
async def index():
    blocked = dns_manager.check_blocking()
    blocked["timer"] = round(blocked["timer"])

    return await render_template(
        "index.html",
        blocked=blocked,
    )


@app.route("/enable")
def enable():
    dns_manager.enable_blocking()

    return redirect(url_for("index"))


@app.route("/disable", methods=("POST", "GET"))
@app.route("/disable/<period>")
async def disable(period: str=""):
    if request.method == "POST":
        form = await request.form
        period = _clean_period_value(float(form["period"]))
        if form.get("device") == "y":
            app.add_background_task(pihole_controller.disable_client, form["ip-addr"], period)
        elif period > 0:
            dns_manager.disable_blocking(period)

        return redirect(url_for("index"))

    if period:
        dns_manager.increase_disable_period(_clean_period_value(int(period)))

        return redirect(url_for("index"))

    return await render_template("disable.html")


@app.route("/status")
def status() -> dict:
    return dns_manager.check_blocking()


@app.route("/client")
def client() -> dict[str, str]:
    return ClientPiholeManager.get_client_ip(API_URL)
