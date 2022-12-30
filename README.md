# Control Panel
This is a basic web UI attached to a systemd backend for starting and stopping systemd services.

It also exposes some information about the timers for the status page to use: https://github.com/banool/status.

## Local development
First, install pystemd. Pretty much just follow the guide here: https://github.com/facebookincubator/pystemd.

Then, do this:
```
PORT=9991 UNITS_TO_CONTROL=minecraft,factorio TIMER_UNITS_TO_IGNORE=shadow.service ./run.sh
```

## Deployment
Just use banool/server-setup.
