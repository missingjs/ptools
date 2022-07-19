FROM ubuntu:20.04

RUN apt-get update \
        && apt-get install -y nginx curl python3

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/trojan-gfw/trojan-quickstart/master/trojan-quickstart.sh)" || true

ARG domain
ARG email
ARG password

COPY . /root/

RUN /bin/bash /root/install.sh -d "${domain}" -e "${email}" -p "${password}"

ENTRYPOINT ["/root/entry-point.sh"]

