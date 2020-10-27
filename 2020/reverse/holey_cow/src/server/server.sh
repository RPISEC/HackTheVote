#!/bin/bash

while true; do
    socat -d -d -s TCP-LISTEN:9000,reuseaddr,fork EXEC:"stdbuf -i0 -o0 ./chal"
    sleep 1;
done

