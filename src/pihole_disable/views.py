from quart import Response, redirect, render_template, request, url_for

from pihole_disable.main import API_PASSWORD, API_URL, app
from pihole_disable.pihole_control import (
    AuthManager,
    PiholeController,
)
from pihole_disable.utils import _check_client, _clean_period_value

auth_manager = AuthManager(API_URL, API_PASSWORD)
pihole_controller = PiholeController(auth_manager)
dns_manager = pihole_controller.get_dns_manager()


@app.route("/")
async def index():
    blocked = dns_manager.check_blocking()
    blocked["timer"] = round(blocked["timer"])

    return await render_template(
        "index.html",
        blocked=blocked,
    )


@app.route("/enable")
@app.route("/enable/<_client>")
async def enable(_client: str = "") -> Response:
    if _client:
        await pihole_controller.enable_client(_client)
    else:
        dns_manager.enable_blocking()

    return redirect(url_for("index"))


@app.route("/disable", methods=("POST", "GET"))
@app.route("/disable/<int:period>")
@app.route("/disable/<int:period>/<_client>")
async def disable(period: int = 0, _client: str = "") -> Response | str:
    if request.method == "POST":
        form = await request.form
        period = _clean_period_value(form["period"])
        _client = form["ip-addr"]
        if form.get("device") == "y":
            if _check_client(_client):
                app.add_background_task(
                    pihole_controller.disable_client, _client, period
                )
        elif period > 0:
            dns_manager.disable_blocking(period)

        return redirect(url_for("index"))

    if period:
        if _check_client(_client):
            app.add_background_task(
                pihole_controller.increase_disable_period, _client, period
            )
        else:
            dns_manager.increase_disable_period(period)

        return redirect(url_for("index"))

    return await render_template("disable.html")


@app.route("/status")
def status() -> dict[str, bool | int]:
    return dns_manager.check_blocking()


@app.route("/client/<_client>")
def client(_client: str = "") -> dict[str, str | bool | int]:
    period = pihole_controller.query_client_remaining_period(_client)

    return {"ip": _client, "blocking": period == 0, "timer": period}
