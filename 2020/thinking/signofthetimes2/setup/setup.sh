#!/bin/bash

set -e

apt-get update -y 
apt-get install -y python2.7 python-pip socat
pip install pyelftools==0.25 pycrypto==2.6.1 capstone

# Set up the user who will be running the app groupadd -g 1337 app
groupadd -g 31337 app2
useradd -g app2 -m -u 31337 app2 -s /bin/bash

cat > /etc/systemd/system/signofthetimes2.service <<EOF
[Unit]
Description=Sign Of The Times 2
After=network.target

[Service]
Type=simple
User=app2
WorkingDirectory=/home/app2/server
ExecStart=/bin/bash server.sh 
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF


cp -r ./src /home/app2/.

cd /home/app2/server
python <<EOF
from Crypto.PublicKey import RSA
key = RSA.generate(2048)
with open('real_key','wb') as f:
    f.write(key.exportKey('PEM'))
pubkey = key.publickey()
with open('real_key.pub','wb') as f:
    f.write(pubkey.exportKey('PEM'))
EOF

chown root:app2 -R /home/app2

chown root:nogroup /home/app2/server/src/run_elf
chmod o+x /home/app2/server/src/run_elf
chmod +s /home/app2/server/src/run_elf

chmod o-rwx -R /home/ubuntu

systemctl daemon-reload
systemctl enable signofthetimes2
systemctl start signofthetimes2
