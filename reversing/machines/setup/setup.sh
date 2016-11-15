#!/bin/bash

sudo apt install socat python -y

# socat -d -d TCP-LISTEN:9000,reuseaddr,fork EXEC:"python checker.py"
