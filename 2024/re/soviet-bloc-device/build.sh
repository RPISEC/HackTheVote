#!/bin/bash

set -e

DEPLOY_FILES=(
    "./build/challenge"
    "./src/server/server.py"
)

mkdir -p build
mkdir -p deploy

# Build binaries
gcc src/challenge.c -Wall -s -O3 -o build/challenge

# Copy required files to deploy
for f in "${DEPLOY_FILES[@]}"; do
    cp -r "$f" deploy/
done
