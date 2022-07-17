#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir

source setup_env.sh || exit

cd image || exit

docker build -t $IMAGE_NAME \
    --build-arg "domain=$DOMAIN" \
    --build-arg "email=$EMAIL" \
    --build-arg "password=$PASSWORD" \
    .

