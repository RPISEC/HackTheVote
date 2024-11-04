#!/bin/sh

set -ex

DATA_DIR=/tmp/graph
ADMIN_DIR=$DATA_DIR/872bfdd01752ea2641a3e211db6127a7af1d9b44f1602780bbae465ccf4ac25e

cd /src/flaggen
PATH="$DATA_DIR/bin:$PATH" python3 flag2csv.py

mkdir $ADMIN_DIR
cp flag1.csv $ADMIN_DIR
cp flag1.png $ADMIN_DIR
cp flag2.png $ADMIN_DIR


# docker throws an error if I put this in the Dockerfile, so it's here, even though it doesn't really go here
cp /usr/bin/busybox /tmp/graph/bin/sh
