# Control Panel
This is a basic web UI attached to a systemd backend for starting and stopping systemd services.

## Local development
First, install psystemd. Pretty much just follow the guide here: https://github.com/facebookincubator/pystemd.

Then, do this:
```
python3 -m venv myvenv
. myvenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pystemd
```
