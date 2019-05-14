FROM ubuntu:latest

ADD redis-3.0.7.tgz /usr/bin
COPY entrypoint.sh /
COPY create-stunnel.py sugariq-redis-migrate.py /tmp/


RUN apt update && \
    apt install -y python python-pip net-tools inetutils-ping emacs-nox stunnel time vim && \
    pip install redis

ENTRYPOINT /entrypoint.sh


