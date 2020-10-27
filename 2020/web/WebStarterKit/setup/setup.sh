#!/bin/bash

alarm() { perl -e 'alarm shift; exec @ARGV' "$@"; }

timeout()
{
    time=$1; shift
    "$@"& pid=$!
    ( sleep $time; kill $! )&
    wait $pid && kill $!
}

while [ true ]
do
    if [ -d chal ]; then
        chmod -R 755 chal
        rm -rf chal
    fi

    mkdir chal
    cd chal
    unzip ../chal.zip
    timeout 3600 ./start.sh
    killall -9 "Torque Demo Debug OSX"
    cd ..

    echo "Restarting..."
    sleep 5
done

