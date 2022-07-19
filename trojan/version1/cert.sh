#!/bin/bash

usage()
{
    local cmd=$(basename $0)
    cat >&2 << EOF
usage: $cmd register|renew
EOF
    exit 1
}

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir
source setup_env.sh || exit

subcmd=$1

function do_register()
{
    docker run --rm \
        --network host \
        -v "$self_dir/volumns/cert/:/etc/letsencrypt/:rw" \
        -v "$self_dir/volumns/log/:/var/log/letsencrypt/:rw" \
        certbot/certbot:latest \
            certonly --standalone \
            --email "$EMAIL" \
            --agree-tos \
            --no-eff-email \
            -d "$DOMAIN"
}

function do_renew()
{
    docker run --rm \
        --network host \
        -v "$self_dir/volumns/cert/:/etc/letsencrypt/:rw" \
        -v "$self_dir/volumns/www/:/var/www/html/:rw" \
        -v "$self_dir/volumns/log/:/var/log/letsencrypt/:rw" \
        certbot/certbot:latest \
            renew --webroot -w /var/www/html
}

case $subcmd in
    register)
        do_register
        ;;
    renew)
        do_renew
        ;;
    *)
        usage
        ;;
esac

