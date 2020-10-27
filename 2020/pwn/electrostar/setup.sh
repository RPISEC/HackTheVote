#!/bin/bash

set -e

apt-get update -y 
apt-get install -y socat

# Set up the user who will be running the app groupadd -g 1337 app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/electrostar.service <<EOF
[Unit]
Description=Electrostar
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/
ExecStart=/bin/bash serve.sh
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

cp -r ./bin /home/app/.
cp -r ./serve.sh /home/app/.

chown root:app -R /home/app
chmod -r /home/app/bin/flag3.exe

chmod o-rwx -R /home/ubuntu

systemctl daemon-reload
systemctl enable electrostar
systemctl start electrostar
