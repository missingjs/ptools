#!/bin/bash


BEGIN_DATE=2016-12-01
END_DATE=2017-05-31

D=$BEGIN_DATE
E=$(date +%s -d "$END_DATE")

logdir=
outputdir=

source ./locks.sh

while [ $(date +%s -d $D) -le $E ]; do
    if [ -e stop_filter ]; then
        echo "stop_filter detected, exit job"
        exit
    fi

    logfile=$logdir/log.$D.local3.zip
    outfile=$outputdir/log.$D.info.gz
    donefile=$outputdir/log.$D.done

    job_script="
        if [ -e $donefile ]; then
            echo $donefile exist, skip
            exit 0
        fi
        flock -x outputlock echo [BEGIN] $logfile \$(date)
        unzip -cq $logfile | grep --text 'tkprop=' | gzip > $outfile
        touch $donefile
        flock -x outputlock echo [END] $logfile \$(date)
    "

    lock=`do_lock`
    flock -x $lock bash -c "$job_script" &

    D=$(date "+%Y-%m-%d" -d "$D +1 days")
done

ensure_finish

