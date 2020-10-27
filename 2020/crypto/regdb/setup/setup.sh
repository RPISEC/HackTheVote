#!/bin/bash

# This is how I (itszn) set this app up

set -e

apt-get update -y
apt-get install -y python3 python3-pip

pip3 install cryptography

# Set up the user who will be running the app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/regdb.service <<EOF
[Unit]
Description=regdb
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/src
ExecStart=/usr/bin/python3 server.py socket
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

cp -r ./src /home/app/.
chown root:app -R /home/app/
chmod og-w -R /home/app/

chmod -R o-rwx /home/ubuntu

systemctl daemon-reload
systemctl enable regdb
systemctl start regdb
