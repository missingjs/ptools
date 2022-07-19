#!/bin/bash

usage()
{
    local cmd=$(basename $0)
    cat << EOF
usage: 
    $cmd setup   place static web content
    $cmd index   find web content, then write directory to index file
EOF
    exit 1
}

self_dir=$(cd $(dirname $0) && pwd)

cd $self_dir

source common.sh || exit
source setup_env.sh || exit

[ -z $volume_directory ] && config_missing volume_directory

index_file=_web_dirs.index
dest_dir=$volume_directory/var/www/html

subcmd=$1

[ -z $subcmd ] && usage

function find_web_content()
{
    [ -z $web_source ] && config_missing web_source
    python3 findweb.py "$web_source" "$web_source_blacklist" > $index_file
}

function setup_web_content()
{
    [ -e $index_file ] || find_web_content
    local source_dir=$(python3 -c "import random; fp=open('$index_file'); print(random.choice(fp.readlines()).strip()); fp.close()")
    rm -rf $dest_dir/* || exit
    cp -r $source_dir/* $dest_dir/
}

case $subcmd in
    setup)
        setup_web_content
        ;;
    index)
        find_web_content
        ;;
    *)
        usage
        ;;
esac
