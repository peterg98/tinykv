#!/bin/bash -e
export VOLUMES=${1:-localhost:3001} # default volume=1
export DB=${2:-/tmp/cachedb/}
export TYPE=master

uwsgi --disable-logging --http :${PORT:-3000} --wsgi-file /src/master.py --callable master --master --processes 4