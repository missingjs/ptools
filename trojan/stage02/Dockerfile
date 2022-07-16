FROM trojan-s01:latest

ARG domain
ARG email
ARG password

COPY . /root/

WORKDIR /root/trojan-deploy

RUN bash install.sh -d "${domain}" -e "${email}" -p "${password}"

ENTRYPOINT ["/root/trojan-deploy/entry-point.sh"]

