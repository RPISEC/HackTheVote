#!/bin/sh

set -e

sed -i "s/PLACEHOLDER_FLAG/$FLAG/" nsjail.conf
unset FLAG

exec nsjail --config nsjail.conf "$@"
