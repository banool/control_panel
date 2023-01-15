# Control Panel
This is a basic web UI attached to a systemd backend for starting and stopping systemd services.

It also exposes some information about the timers for the status page to use: https://github.com/banool/status. The status for all timers is `AND`ed and made available at `/timers_overall`, which can then be plugged into the uptime monitor to check whether the timers are working.

## Local development
First, install pystemd. Pretty much just follow the guide here: https://github.com/facebookincubator/pystemd.

Then, do this:
```
PORT=9991 UNITS_TO_CONTROL=minecraft,factorio TIMER_UNITS_TO_IGNORE=shadow.service ./run.sh
```

## Deployment
Just use banool/server-setup.
