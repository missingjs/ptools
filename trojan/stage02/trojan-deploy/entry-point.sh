#!/bin/bash

service nginx start

/usr/local/bin/trojan /usr/local/etc/trojan/config.json

