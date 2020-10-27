#!/bin/bash

set -e

apt-get update -y 
apt-get install -y python2.7 python-pip socat
pip install pyelftools==0.25 pycrypto==2.6.1 capstone

# Set up the user who will be running the app groupadd -g 1337 app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/signofthetimes.service <<EOF
[Unit]
Description=Sign Of The Times
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/server
ExecStart=/bin/bash server.sh 
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF


cp -r ./src /home/app/server

cd /home/app/server
python <<EOF
from Crypto.PublicKey import RSA
key = RSA.generate(2048)
with open('real_key','wb') as f:
    f.write(key.exportKey('PEM'))
pubkey = key.publickey()
with open('real_key.pub','wb') as f:
    f.write(pubkey.exportKey('PEM'))
EOF

chown root:app -R /home/app

chown root:nogroup /home/app/server/src/run_elf
chmod o+x /home/app/server/src/run_elf
chmod +s /home/app/server/src/run_elf

chmod o-rwx -R /home/ubuntu

systemctl daemon-reload
systemctl enable signofthetimes
systemctl start signofthetimes
