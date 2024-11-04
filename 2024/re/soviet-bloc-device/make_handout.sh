#!/bin/bash

set -e

HANDOUT_FILES=(
    "/home/challenge_user/deploy/challenge"
    "/home/challenge_user/deploy/server.py"
)

mkdir -p /handout

# Copy required files to handout
for f in "${HANDOUT_FILES[@]}"; do
    cp -r "$f" /handout/
done
