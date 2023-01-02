#!/bin/bash

set -e

cd "$(dirname "$0")"

# Assert PORT was set.
if [[ -z "${PORT}" ]]; then
    echo "ERROR: Please set the PORT environment variable"
    exit 1
fi

# If the virtual environment doesn't exist, make it.
if [ ! -d "myvenv" ]; then
    python3 -m venv myvenv
fi

# Source the venv.
. myvenv/bin/activate

# Install dependencies if necessary.
pip install --upgrade pip
pip install -r requirements.txt
pip install git+https://github.com/facebookincubator/pystemd.git@b39622ed0da502394f17df202ab21ca1089704bc

# Run gunicorn.
gunicorn -w 2 -b 127.0.0.1:$PORT app:app
