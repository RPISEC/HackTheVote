#!/bin/bash

sudo apt install socat python

# socat -d -d TCP-LISTEN:9000,reuseaddr,fork EXEC:"python -u check_solution.py"
