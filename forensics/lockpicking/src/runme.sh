#!/usr/bin/env bash

# Generate the 7z
cd truecrypt
./make_7z.sh
cd ..

# Generate the final chal
python genchallenge.py

# Cleanup
rm -f picks_lsb.png
rm -f truecrypt/S3CR3T.7z
