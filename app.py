#!/usr/bin/env python

from flask import Response
from lib import *

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)
LOG.setLevel("DEBUG")

app = Flask(__name__)


units_to_control = get_units_to_control()


@app.route("/")
def index():
    unit_to_status = get_unit_to_status(units_to_control)
    LOG.info(f"index: Unit to status: {unit_to_status}")
    return render_template("index.html.j2", unit_to_status=unit_to_status)


@app.route("/start/<unit>", methods=["POST"])
def start(unit):
    LOG.info(f"start: Received request to start: {unit}")
    validate_unit_allowed(unit, units_to_control)
    start_unit(unit)
    LOG.info(f"Asked systemd to start: {unit}")
    return redirect(url_for("index"))


@app.route("/stop/<unit>", methods=["POST"])
def stop(unit):
    LOG.info(f"stop: Received request to start: {unit}")
    validate_unit_allowed(unit, units_to_control)
    stop_unit(unit)
    LOG.info(f"Asked systemd to stop: {unit}")
    return redirect(url_for("index"))


@app.route("/timers", methods=["GET"])
def timers():
    LOG.info(f"timers: Received request for timer info")
    timer_units_to_report = get_timer_units_to_report()
    info = get_many_last_run_info(timer_units_to_report)
    LOG.info(f"timers: Returning timer info: {info}")
    return info


@app.route("/timers_overall", methods=["GET"])
def timers_overall():
    LOG.info(f"timers: Received request for overall timer info")
    timer_units_to_report = get_timer_units_to_report()
    info = get_many_last_run_info(timer_units_to_report)
    all_successful = all(s == 0 for s in [i["ExecMainStatus"] for i in info.values()])
    if all_successful:
        message = "For each timer, the most recent run was successful 🤠"
        status = 200
    else:
        message = "The last run of one of the timers was not successful 😭"
        status = 500
    LOG.info(f"timers: Returning status {status} based on info {info}")
    return Response(message, status=status)
