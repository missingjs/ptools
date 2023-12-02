#!/bin/bash

project_name=trojan-proxy
self_dir=$(cd $(dirname $0) && pwd)
cd $self_dir

docker compose -f docker-compose.yml -p $project_name "$@"
