#!/bin/bash

set -x
docker stop trojan02

docker container rm trojan02

docker run -d --network host --name trojan02 trojan-s02:latest 

