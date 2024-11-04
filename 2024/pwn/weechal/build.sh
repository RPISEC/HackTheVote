#!/bin/bash

set -e

wget https://github.com/weechat/weechat/archive/refs/tags/v3.4.zip
unzip v3.4.zip
cd /weechat-3.4
patch -u -p1 </src/chal.patch
mkdir build
cmake -B build \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_PREFIX=/weechat \
    -DENABLE_ALIAS=OFF \
    -DENABLE_BUFLIST=OFF \
    -DENABLE_CHARSET=OFF \
    -DENABLE_FIFO=OFF \
    -DENABLE_FSET=OFF \
    -DENABLE_GUILE=OFF \
    -DENABLE_IRC=OFF \
    -DENABLE_LOGGER=OFF \
    -DENABLE_LUA=OFF \
    -DENABLE_PERL=OFF \
    -DENABLE_PHP=OFF \
    -DENABLE_PYTHON=OFF \
    -DENABLE_RUBY=OFF \
    -DENABLE_SCRIPT=OFF \
    -DENABLE_SCRIPTS=OFF \
    -DENABLE_SPELL=OFF \
    -DENABLE_TCL=OFF \
    -DENABLE_TRIGGER=OFF \
    -DENABLE_TYPING=OFF \
    -DENABLE_XFER=OFF
cmake --build build
cmake --install build
cd ..
rm -rf weechat-3.4

mkdir -p /build /handout

chmod +x src/challenge

# Copy required files to handout
cp src/challenge /handout
cp src/chal.patch /handout
mkdir -p /handout/weechat/lib/weechat/plugins/
mkdir -p /handout/weechat/bin/
# much easier with this plugin ofc
# cp "/weechat/lib/weechat/plugins/exec.so"   "/handout/weechat/lib/weechat/plugins/exec.so"
cp "/weechat/lib/weechat/plugins/relay.so"  "/handout/weechat/lib/weechat/plugins/relay.so"
cp "/weechat/bin/weechat"                   "/handout/weechat/bin/weechat"
cp "/weechat/bin/weechat-curses"            "/handout/weechat/bin/weechat-curses"
cp "/weechat/bin/weechat-headless"          "/handout/weechat/bin/weechat-headless"

