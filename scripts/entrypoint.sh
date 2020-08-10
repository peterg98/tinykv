#!/bin/bash

/scripts/shard.sh PORT=3001 DIR=/tmp/shard1/ &
/scripts/shard.sh PORT=3002 DIR=/tmp/shard2/ &
/scripts/master.sh localhost:3001,localhost:3002 /tmp/cachedb/ # start master server and 