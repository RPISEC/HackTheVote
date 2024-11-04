#!/bin/bash

set -e

DEPLOY_FILES=(
    "./src/chall.py"
    "./src/bzImage"
    "./src/rootfs.cpio.gz"
)

mkdir -p deploy


# Copy required files to deploy
for f in "${DEPLOY_FILES[@]}"; do
    cp -r "$f" deploy/
done
