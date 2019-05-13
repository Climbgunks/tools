FROM ubuntu:latest

ADD redis-3.0.7.tgz /usr/bin
COPY entrypoint.sh /
COPY create-stunnel.py /usr/bin

RUN apt update && \
    apt install -y python net-tools inetutils-ping emacs-nox

ENTRYPOINT /entrypoint.sh


