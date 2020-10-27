#!/bin/sh
set -e
sudo apt update
sudo apt upgrade
sudo apt install socat
groupadd -g 1337 app
useradd -g app -u 1337 app -s /bin/bash

cat > /etc/systemd/system/primary.service <<EOF
[Unit]
Description=primary
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=socat TCP-LISTEN:1337,fork,reuseaddr EXEC:./primaries
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

mv setup /server
rm -fr src
chown root:app -R /server/*

systemctl daemon-reload
systemctl enable primary
systemctl start primary
