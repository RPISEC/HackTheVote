#!/bin/bash

set -e

DEPLOY_FILES=(
    "./build/challenge"
)

mkdir -p build
mkdir -p deploy

# Build binaries
gcc src/challenge.c -Wall -o build/challenge

# Copy required files to deploy
for f in "${DEPLOY_FILES[@]}"; do
    cp -r "$f" deploy/
done
