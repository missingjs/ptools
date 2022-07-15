FROM trojan-s01:latest

COPY . /root/

WORKDIR /root/trojan-deploy

RUN bash install.sh

ENTRYPOINT ["/root/trojan-deploy/entry-point.sh"]

