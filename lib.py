#!/usr/bin/env python

import contextlib
import logging
import os
import sys

from flask import abort, redirect, render_template, Flask, url_for
from pystemd.systemd1 import Unit
from pystemd.dbuslib import DBus

LOG = logging.getLogger(__name__)


def get_units_to_control():
    try:
        return os.environ["UNITS_TO_CONTROL"].split(",")
    except KeyError:
        raise RuntimeError("Please set UNITS_TO_CONTROL env var")


@contextlib.contextmanager
def get_unit(unit, unit_type="service"):
    try:
        with DBus(user_mode=True) as dbus:
            u = Unit(f"{unit}.{unit_type}".encode("utf-8"), bus=dbus)
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


def validate_unit_allowed(unit, units_to_control):
    if unit not in units_to_control:
        abort(400, f"Unit {unit} is not allowlisted")
