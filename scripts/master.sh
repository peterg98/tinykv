#!/bin/bash -e
export SHARDS=${1:-localhost:3001}
export DB=${2:-/tmp/cachedb/}
export TYPE=master

uwsgi --disable-logging --http :${PORT:-3000} --wsgi-file /tmp/master.py --callable master --master --processes 4