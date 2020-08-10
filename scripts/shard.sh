#!/bin/bash -e
export SHARD=${1:-/tmp/shard1/}
export TYPE=shard
export PORT =${PORT:-3001}

for I in 0 1 2 3 4 5 6 7 9 a b c d e
    mkdir -m 777 -p $VOLUME/${I}{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}/{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}
done
# Create dynamic nginx.conf's for multiple shards. Each shard has its own server

CONF=$(mktemp)
echo "
daemon off;
worker_processes auto;

error_log /dev/stderr;
pid $SHARD/nginx.pid;

events {
    multi_accept on;
    worker_connections 4096;
}

http {
     sendfile on;
    sendfile_max_chunk 1024k;

    tcp_nopush on;
    tcp_nodelay on;

    open_file_cache off;
    types_hash_max_size 2048;

    server_tokens off;

    default_type application/octet-stream;

    server {
        listen $PORT default_server;
        location / {
        root $SHARD;

        client_body_temp_path $SHARD/body_temp;
        client_max_body_size 0;

        dav_methods PUT DELETE;
        dav_access group:rw all:r;
    }
  }
}
" > $CONF
nginx -c $CONF -p $SHARD/tmp