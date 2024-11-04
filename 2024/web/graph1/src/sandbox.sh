#!/bin/sh
userdir=$(basename "$PWD")
cmd="$@"
unshare -r chroot /tmp/graph sh -c "cd $userdir && $cmd"
