#!/bin/sh

set -e

sudo apt update
sudo apt upgrade
sudo apt install socat

groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/flipstate.service <<EOF
[Unit]
Description=flipstate
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=socat -d -d -s TCP-LISTEN:43690,reuseaddr,fork EXEC:"python3 -u ./chal.py"
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

mv src /server
chown root:app -R /server/*

systemctl daemon-reload
systemctl enable flipstate
systemctl start flipstate
