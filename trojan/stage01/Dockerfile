FROM ubuntu:20.04

RUN apt update \
        && apt install -y snapd nginx cron curl

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/trojan-gfw/trojan-quickstart/master/trojan-quickstart.sh)" || true

