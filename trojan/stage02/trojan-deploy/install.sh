#!/bin/bash

function usage()
{
    local cmd=$(basename $0)
    cat >&2 << EOF
usage: $cmd -d <domain> -e <email> -p <password>
EOF
    exit 1
}

while getopts ':d:e:p:' option; do
    case $option in
        d)
            domain="$OPTARG"
            ;;
        e)
            email="$OPTARG"
            ;;
        p)
            password="$OPTARG"
            ;;
        \?)
            usage
            ;;
    esac
done

[ -z "$domain" -o -z "$email" -o -z "$password" ] && usage

ip=$(python3 -c "import socket; print(socket.gethostbyname('$domain'))")
[ -z "$ip" ] && { echo "failed to get ip of domain $domain">&2; exit 2; }

self_dir=$(cd $(dirname $0) && pwd)
cd $self_dir

set -e

cat >/etc/nginx/sites-available/default << 'EOF'
server {
    listen 127.0.0.1:80 default_server;
    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;
    server_name _;
    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        try_files $uri $uri/ =404;
    }
}
EOF

cat >/etc/nginx/sites-available/$domain << EOF
server {
    listen 127.0.0.1:80;
    server_name $ip;
    return 301 https://$domain\$request_uri;
}

server {
    listen 0.0.0.0:80;
    listen [::]:80;
    server_name _;
    return 301 https://\$host\$request_uri;
}
EOF

ln -s /etc/nginx/sites-available/$domain /etc/nginx/sites-enabled/

pycode="
import json
import os
import sys
password = sys.argv[1]
trojan_config = '/usr/local/etc/trojan/config.json'
with open(trojan_config, 'rt') as ifp:
    conf = json.load(ifp)
    conf['password'] = [password]
    conf['ssl']['cert'] = '/etc/letsencrypt/live/$domain/fullchain.pem'
    conf['ssl']['key'] = '/etc/letsencrypt/live/$domain/privkey.pem'

save_file = '/usr/local/etc/trojan/config.json.tmp'
with open(save_file, 'wt') as ofp:
    json.dump(conf, ofp, indent=4)

os.rename(save_file, trojan_config)
"

python3 -c "$pycode" "$password"

certbot certonly --standalone --email "$email" --agree-tos --no-eff-email -d "$domain"

