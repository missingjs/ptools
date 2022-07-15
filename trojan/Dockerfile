FROM ubuntu:20.04

RUN apt update \
    && apt install -y snapd nginx \
    && snap install core \
    && snap refresh core \
    && snap install --classic certbot \
    && ln -s /snap/bin/certbot /usr/bin/certbot

COPY nginx/default /etc/nginx/sites-available/default

