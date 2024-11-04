#!/bin/bash

wget https://github.com/weechat/weechat/archive/refs/tags/v3.4.zip
unzip v3.4.zip

tmux splitw -h "python3 ./solve.py 172.17.0.1:31337 ; bash"
# tmux splitw -h "python3 ./solve.py 10.242.3.149:12345 ; bash"
bash
