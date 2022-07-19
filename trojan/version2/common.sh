this_dir=$(cd -P $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)

function config_missing()
{
    local name=$1
    echo "$1 not configured" >&2
    exit 1
}


