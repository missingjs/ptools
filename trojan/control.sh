#!/bin/bash

usage()
{
    local cmd=$(basename $0)
    cat >&2 << EOF
usage: $cmd create|start|stop|restart
EOF
    exit 1
}

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir

source setup_env.sh || exit

action=$1

[ -z "$action" ] && usage

function do_start()
{
    docker container start $CONTAINER_NAME
}

function do_stop()
{
    docker container stop $CONTAINER_NAME
}

function do_create()
{
    docker run -d --network host \
        --name $CONTAINER_NAME \
        -v "$self_dir/volumns/cert/:/etc/letsencrypt/:ro" \
        -v "$self_dir/volumns/www/:/var/www/html/:ro" \
        $IMAGE_NAME:latest 
}

case $action in
    create)
        do_create
        ;;
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_stop
        do_start
        ;;
    *)
        usage
        ;;
esac

