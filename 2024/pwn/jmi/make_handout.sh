#!/bin/bash

set -e

HANDOUT_FILES=(
    "/home/challenge_user/deploy/challenge"
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
)

mkdir -p /handout

# Copy required files to handout
for f in "${HANDOUT_FILES[@]}"; do
    cp -r "$f" /handout/
done
