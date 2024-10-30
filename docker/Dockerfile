# This docker file is used for local development via docker-compose

FROM docker.arvancloud.ir/python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD requirements/ requirements/
RUN pip install -r requirements/local.txt

RUN mkdir /app
WORKDIR /app
ADD ./ /app/
