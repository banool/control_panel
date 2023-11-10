#!/usr/bin/env python

import contextlib
import logging
import json
import os
import subprocess
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


def get_units_for_timers(userspace=True):
    args = ["systemctl"]
    if userspace:
        args += ["--user"]
    args += ["list-timers", "-o", "json", "--all"]
    out = subprocess.check_output(args, universal_newlines=True)
    j = json.loads(out)
    units = [t["activates"] for t in j]
    return [u for u in units if u]


# This returns the units that the timers activate.
def get_timer_units_to_report():
    timers_to_ignore = []
    with contextlib.suppress(KeyError):
        timers_to_ignore = os.environ["TIMER_UNITS_TO_IGNORE"].split(",")
    timers_to_ignore = set(timers_to_ignore)

    if not all(t.endswith(".service") for t in timers_to_ignore):
        raise RuntimeError(
            "TIMER_UNITS_TO_IGNORE should contain unit names ending with.service, not timer names"
        )

    units = []
    units += [(u, True) for u in get_units_for_timers(userspace=True)]
    units += [(u, False) for u in get_units_for_timers(userspace=False)]

    out = []
    for u in units:
        if u[0] in timers_to_ignore:
            continue
        out.append(u)

    return out


def validate_unit_allowed(unit, units_to_control):
    if unit not in units_to_control:
        abort(400, f"Unit {unit} is not allowlisted")


def get_last_run_info(unit, userspace=True):
    if not unit.endswith(".service"):
        raise RuntimeError("Should only be used with .service units")
    properties = [
        "ExecMainStartTimestamp",
        "ExecMainExitTimestamp",
        "ExecMainStatus",
    ]
    args = ["systemctl"]
    if userspace:
        args += ["--user"]
    args += [
        "show",
        unit,
        "--property",
        ",".join(properties),
        "--no-page",
        "--timestamp",
        "unix",
    ]
    out = subprocess.check_output(args, universal_newlines=True)
    d = {}
    for line in out.splitlines():
        key, value = line.split("=")
        with contextlib.suppress(IndexError):
            if value[0] == "@":
                value = value[1:]
        with contextlib.suppress(ValueError):
            value = int(value)
        if value == "":
            continue
        d[key] = value
    return d


# Unit should be a tuple of (unit_name, userspace_bool)
def get_many_last_run_info(units):
    d = {}
    for item in units:
        unit, userspace = item
        d[unit] = get_last_run_info(unit, userspace=userspace)
    return d
