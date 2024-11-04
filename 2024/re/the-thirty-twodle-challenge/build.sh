#!/bin/bash

set -e

DEPLOY_FILES=(
    "./build/challenge"
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib64/ld-linux-x86-64.so.2"
)

mkdir -p build
mkdir -p deploy

# Build binaries
gcc src/challenge.c -g -Wall -DDIFFICULTY=32 -o build/challenge

# Copy required files to deploy
for f in "${DEPLOY_FILES[@]}"; do
    cp -r "$f" deploy/
done
