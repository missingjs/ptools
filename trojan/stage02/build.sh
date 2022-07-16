#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir

source setup_env.sh || exit

docker build -t trojan-s02 \
    --network host \
    --build-arg "domain=$DOMAIN" \
    --build-arg "email=$EMAIL" \
    --build-arg "password=$PASSWORD" \
    .

