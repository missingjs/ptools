FROM ubuntu:20.04

RUN apt-get update \
        && apt-get install -y nginx curl certbot python3

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/trojan-gfw/trojan-quickstart/master/trojan-quickstart.sh)" || true

