FROM python:3.8-buster

RUN apt-get update
RUN apt-get install build-essential python-dev nginx -y
RUN pip install uwsgi Flask

COPY ./nginx.conf /etc/nginx/nginx.conf

CMD uwsgi --http-socket :3031 --wsgi-file /src/server.py --callable app --processes 4 --threads 2 --stats :9191