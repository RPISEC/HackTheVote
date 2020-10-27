#!/usr/bin/env bash

mv tc.mp4 S3CR3T
7z a -p$(sed -r 's/\s//g' pass.txt) -mhe=on S3CR3T.7z S3CR3T
mv S3CR3T tc.mp4
