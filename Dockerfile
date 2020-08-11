FROM python:3.8-buster

RUN apt-get update
RUN apt-get install build-essential python-dev nginx libffi-dev curl -y

RUN pip install uwsgi Flask lmdb requests

COPY ./cfg/nginx.conf /etc/nginx/nginx.conf
COPY ./scripts /scripts
COPY ./src /tmp

RUN chmod +x /scripts/entrypoint.sh

ENTRYPOINT [ "/scripts/entrypoint.sh" ]