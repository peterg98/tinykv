FROM python:3.8-buster

RUN apt-get update
RUN apt-get install build-essential python-dev nginx -y

RUN wget http://download.redis.io/redis-stable.tar.gz
RUN tar xvzf redis-stable.tar.gz
RUN cd redis-stable
RUN make

RUN pip install uwsgi Flask redis

COPY ./cfg/nginx.conf /etc/nginx/nginx.conf
COPY ./cfg/uwsgi.ini .
COPY ./cfg/entrypoint.sh .

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]