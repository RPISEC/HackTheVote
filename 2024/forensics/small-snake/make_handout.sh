#!/bin/bash

set -e

HANDOUT_FILES=(
)

mkdir -p /handout

# Copy required files to handout
for f in "${HANDOUT_FILES[@]}"; do
    cp -r "$f" /handout/
done
