#!/bin/bash

set -e

mkdir -p /handout
mkdir -p /handout/src

# Copy required files to handout
cp /home/challenge_user/deploy/src/src/main.rs /handout/src/main.rs
cp /home/challenge_user/deploy/src/Cargo.toml /handout/Cargo.toml
