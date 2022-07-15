#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

cp nginx/default /etc/nginx/sites-available/default

