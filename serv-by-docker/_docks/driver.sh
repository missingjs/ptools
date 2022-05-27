#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

usage()
{
    local cmd=$(basename $0)
    cat << EOF
usage:
    $cmd <serv-name> <sub-command> [options]

sub-commands:
    create
        create docker container

    start 
        start container

    stop 
        stop container

    bash [options]
        execute command in container, or open a login shell (no options)
EOF
    exit 1
}

serv_name=$1
subcmd=$2

[ -z "$serv_name" -o -z "$subcmd" ] && usage

serv_script="$self_dir/${serv_name}-serv"
container_name="$($serv_script container-name)"

case $subcmd in
    start)
        docker container start $container_name
        ;;
    stop)
        docker container stop -t 3 $container_name
        ;;
    bash)
        shift; shift;
        if [ ${#@} -eq 0 ]; then
            docker exec -u root -it $container_name /bin/bash
        else
            docker exec -u root -it $container_name "$@"
        fi
        ;;
    *)
        shift;
        $serv_script $subcmd "$@"
        ;;
esac

