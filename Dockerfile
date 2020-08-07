FROM python:3.8-buster

RUN apt-get update
RUN apt-get install build-essential python-dev nginx -y
RUN pip install uwsgi Flask

COPY ./cfg/nginx.conf /etc/nginx/nginx.conf
COPY ./cfg/uwsgi.ini .
COPY ./cfg/entrypoint.sh .

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]