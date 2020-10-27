#!/bin/sh
python solve.py | ncat --no-shutdown flipstate.hackthe.vote 43690
