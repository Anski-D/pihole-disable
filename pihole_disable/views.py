from flask import render_template, redirect, url_for, request

from pihole_disable import app, API_URL, API_PASSWORD
from pihole_disable.pihole_disable import PiholeDisabler

disabler = PiholeDisabler(API_URL, API_PASSWORD)


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
