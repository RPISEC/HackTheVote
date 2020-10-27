#!/bin/bash

while true; do
    socat -d -d -s TCP-LISTEN:9001,reuseaddr,fork EXEC:"stdbuf -i0 -o0 ./app.py"
    sleep 1;
done

