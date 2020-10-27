#!/bin/sh
set -e

groupadd -g 1337 app
useradd -g app -u 1337 app -s /bin/bash

cat > /etc/systemd/system/voterfraud_squared.service <<EOF
[Unit]
Description=voterfraud_squared
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=/server/launcher ./rootkit ./flag.txt
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

mv setup /server
rm -r src
chown root:app -R /server/*

systemctl daemon-reload
systemctl enable voterfraud_squared
systemctl start voterfraud_squared

