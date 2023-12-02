#!/bin/bash

self_dir=$(cd $(dirname $0) && pwd)

job="
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
SHELL=/bin/bash
# cert renew
0 0 1 */2 * cd $self_dir; bash cert.sh renew; bash service.sh restart -t 10 trojan

# setup web content
0 0 */5 * * $self_dir/webcont.sh setup

# start service after system start
@reboot cd $self_dir; sleep 40; bash service.sh up -d
"

echo "These jobs below will be appended to cron. Please double check !!"
echo "$job"

(crontab -l 2>/dev/null; echo "$job") | crontab -

