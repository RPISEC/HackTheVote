#!/bin/bash
set -e

apt-get update -y
apt-get install -y python3 pocl-opencl-icd gcc g++ make

# Set up the user who will be running the app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/hash.service <<EOF
[Unit]
Description=hash
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=python3 server.py socket
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

git clone https://github.com/hashcat/hashcat.git
cd hashcat
git apply ../setup/patch
make install
cd ..

cp -r src /server
chown root:app -R /server/*
chmod og-w -R /server/*

#chmod -R o-rwx /home/ubuntu

systemctl daemon-reload
systemctl enable hash
systemctl start hash
