#!/bin/bash

/scripts/shard.sh /tmp/shard1/ 3001 &
/scripts/shard.sh /tmp/shard2/ 3002 & 
/scripts/master.sh localhost:3001,localhost:3002 /tmp/cachedb/ # start master server and 