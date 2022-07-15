#!/bin/bash

service nginx start

service cron start

# service trojan start
# tail -f /dev/null

/usr/local/bin/trojan /usr/local/etc/trojan/config.json
