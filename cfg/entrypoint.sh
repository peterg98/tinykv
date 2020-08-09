#!/bin/bash

redis-server
nginx
uwsgi --ini /uwsgi.ini