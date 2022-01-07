#!/usr/bin/env python

import contextlib
import logging
import os
import sys

from flask import abort, redirect, render_template, Flask, url_for
from pystemd.systemd1 import Unit
from pystemd.dbuslib import DBus


LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)
LOG.setLevel("DEBUG")


def get_units_to_control():
    try:
        return os.environ["UNITS_TO_CONTROL"].split(",")
    except KeyError:
        raise RuntimeError("Please set UNITS_TO_CONTROL env var")


@contextlib.contextmanager
def get_unit(unit):
    try:
        with DBus(user_mode=True) as dbus:
            u = Unit(f"{unit}.service".encode("utf-8"), bus=dbus)
            u.load()
            yield u
    finally:
        pass


def get_unit_to_status(units):
    out = {}
    for unit in units:
        with get_unit(unit) as u:
            out[unit] = u.Unit.SubState.decode("utf-8")
    return out


def start_unit(unit):
    with get_unit(unit) as u:
        u.Unit.Start(b"replace")


def stop_unit(unit):
    with get_unit(unit) as u:
        u.Unit.Stop(b"replace")


units_to_control = get_units_to_control()


def validate_unit_allowed(unit):
    if unit not in units_to_control:
        abort(400, f"Unit {unit} is not allowlisted")


app = Flask(__name__)


@app.route("/")
def index():
    unit_to_status = get_unit_to_status(units_to_control)
    LOG.info(f"Unit to status: {unit_to_status}")
    return render_template("index.html.j2", unit_to_status=unit_to_status)


@app.route("/start/<unit>", methods=["POST"])
def start(unit):
    validate_unit_allowed(unit)
    start_unit(unit)
    return redirect(url_for("index"))


@app.route("/stop/<unit>", methods=["POST"])
def stop(unit):
    validate_unit_allowed(unit)
    stop_unit(unit)
    return redirect(url_for("index"))
