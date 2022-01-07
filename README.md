# Control Panel
This is a basic web UI attached to a systemd backend for starting and stopping systemd services.

## Local development
First, install pystemd. Pretty much just follow the guide here: https://github.com/facebookincubator/pystemd.

Then, do this:
```
PORT=9991 UNITS_TO_CONTROL=minecraft ./run.sh
```

## Deployment
Just use banool/server-setup.
