#!/bin/bash

set -e

mkdir -p build
mkdir -p deploy
mkdir -p deploy/src/src

# Build binaries
cargo build --release --manifest-path=src/Cargo.toml

# Copy required files to deploy
cp ./src/target/release/zerovote deploy/challenge
cp ./src/src/main.rs deploy/src/src/main.rs
cp ./src/Cargo.toml deploy/src/Cargo.toml

