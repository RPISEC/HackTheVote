#!/bin/bash

while true; do
    socat -d -d -s TCP-LISTEN:5000,reuseaddr,fork EXEC:"stdbuf -i0 -o0 ./votingbooth"
    sleep 1;
done

