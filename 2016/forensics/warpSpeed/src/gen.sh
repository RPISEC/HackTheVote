#!/usr/bin/env bash

python patch.py
exiftool -all= -xpcomment="I am a square. Anyone who tells you otherwise is a LIAR!" ../handout/warp_speed.jpg
