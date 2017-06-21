get_num_locks()
{
    local num_locks=`cat locks/num_locks`
    if [ -n $num_locks ]; then
        echo $num_locks
    else
        echo 4
    fi
}

find_available()
{
    local j=0
    while [ $j -lt $(get_num_locks) ]; do
        if flock -n locks/mylock_$j echo > /dev/null; then
            echo locks/mylock_$j
            break
        fi
        ((j += 1))
    done
}

do_lock()
{
    L=`find_available`
    while [ -z "$L" ]; do
        sleep 1
        L=`find_available`
    done
    echo $L
}

ensure_finish()
{
    local j=0
    while [ $j -lt $(get_num_locks) ]; do
        flock -x locks/mylock_$j echo > /dev/null
        ((j += 1))
    done
}

sync_echo()
{
    flock -x outputlock echo [$$] "$@"
}


