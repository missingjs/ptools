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

function config_missing()
{
    local name=$1
    echo "$1 not configured" >&2
    exit 1
}

[ -z $domain_name ] && config_missing domain_name
[ -z $email ] && config_missing email

subcmd=$1
VDir=$volume_directory

function do_register()
{
    docker run --rm \
        --network host \
        -v "$VDir/etc/letsencrypt:/etc/letsencrypt:rw" \
        -v "$VDir/var/log/letsencrypt:/var/log/letsencrypt:rw" \
        -v "$VDir/var/lib/letsencrypt:/var/lib/letsencrypt:rw" \
        certbot/certbot:latest \
            certonly --standalone \
            --email "$email" \
            --agree-tos \
            --no-eff-email \
            -d "$domain_name"
}

function do_renew()
{
    docker run --rm \
        --network host \
        -v "$VDir/etc/letsencrypt:/etc/letsencrypt:rw" \
        -v "$VDir/var/log/letsencrypt:/var/log/letsencrypt:rw" \
        -v "$VDir/var/lib/letsencrypt:/var/lib/letsencrypt:rw" \
        -v "$VDir/var/www/html:/var/www/html:rw" \
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

