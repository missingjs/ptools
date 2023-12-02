#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir

source common.sh || exit
source setup_env.sh || exit

[ -z $volume_directory ] && config_missing volume_directory
[ -z $domain_name ] && config_missing domain_name
[ "${#client_passwords[@]}" -eq 0 ] && config_missing client_passwords

[ -d $volume_directory ] || { mkdir -p $volume_directory || exit; }
echo "volume top directory: $volume_directory"

ip=$(python3 -c "import socket; print(socket.gethostbyname('$domain_name'))")
[ -z "$ip" ] && { echo "failed to get ip of domain $domain_name">&2; exit 2; }
echo "ip of $domain_name: $ip"

dir_list="
etc/nginx/conf.d
var/www/html
etc/letsencrypt
var/lib/letsencrypt
var/log/letsencrypt
config
"

cd $volume_directory
for d in $dir_list; do
    [ -d $d ] || { mkdir -vp $d || exit; }
done
cd $self_dir

nginx_service_domain=nginx-server

# nginx default site config
nginx_default=$volume_directory/etc/nginx/conf.d/default.conf
cat >$nginx_default << EOF
server {
    listen 127.0.0.1:80 default_server;
    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;
    server_name _;
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF
echo "DONE $nginx_default"

nginx_domain_site=$volume_directory/etc/nginx/conf.d/$domain_name.conf
cat >$nginx_domain_site << EOF
server {
    listen 127.0.0.1:80;
    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;
    server_name $ip;
    return 301 https://$domain_name\$request_uri;
}

server {
    listen 0.0.0.0:80;
    listen [::]:80;
    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;
    server_name _;
    return 301 https://\$host\$request_uri;
}
EOF
echo "DONE $nginx_domain_site"


# generate trojan configuration
pycode="
import json
import os
import sys
passwords = sys.argv[1:]
trojan_config = '$self_dir/example/server.json-example'
with open(trojan_config, 'rt') as ifp:
    conf = json.load(ifp)
    conf['password'] = passwords
    conf['remote_addr'] = '127.0.0.1'
    conf['ssl']['cert'] = '/etc/letsencrypt/live/$domain_name/fullchain.pem'
    conf['ssl']['key'] = '/etc/letsencrypt/live/$domain_name/privkey.pem'

save_file = '$volume_directory/config/config.json.tmp'
with open(save_file, 'wt') as ofp:
    json.dump(conf, ofp, indent=4)

target_file = '$volume_directory/config/config.json'
os.rename(save_file, target_file)
print(f'DONE {target_file}')
"

python3 -c "$pycode" "${client_passwords[@]}"

VDir=$volume_directory
cat >docker-compose.yml << EOF
version: "3.9"
services:
  $nginx_service_domain:
    image: nginx:latest
    init: true
    network_mode: host
    ports:
      - "80:80"
    volumes:
      - $VDir/etc/nginx/conf.d:/etc/nginx/conf.d:ro
      - $VDir/var/www/html:/var/www/html:ro
  trojan:
    image: trojangfw/trojan:latest
    init: true
    network_mode: host
    ports:
      - "443:443"
    volumes:
      - $VDir/etc/letsencrypt:/etc/letsencrypt:ro
      - $VDir/config:/config:ro
EOF
echo "DONE docker-compose.yml"

