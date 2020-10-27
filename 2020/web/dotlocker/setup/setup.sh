#!/bin/bash

set -e

apt-get update -y
# Install nginx, mongodb, python2, and deps for chromeium
apt-get install -y nginx mongodb libpangocairo-1.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2  libasound2 libatk1.0-0 libgtk-3-0 libxcb-dri3-0 libgbm1 curl python2.7

curl https://bootstrap.pypa.io/get-pip.py --output /tmp/get-pip.py
python2.7 /tmp/get-pip.py

# Set up node for puppeteer
(curl -sL https://deb.nodesource.com/setup_12.x | bash -)
apt-get install -y nodejs
(cd / && npm i puppeteer --unsafe-perm)
#mv node_modules /

# Install python deps
pip2 install pymongo==3.4.0 flask requests gunicorn

# Set up the user who will be running the app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/dotlocker.service <<EOF
[Unit]
Description=Dotlocker
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=/usr/bin/stdbuf -o0 /usr/local/bin/gunicorn -w 4 server:app -b unix:/tmp/gunicorn.sock --user app --access-logfile -
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF


cat > /etc/nginx/sites-available/default <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$http_host;
        proxy_redirect off;

        # proxy to /server/server.py
        proxy_pass http://unix:/tmp/gunicorn.sock;
    }

    location ^~ /static  {
        include /etc/nginx/mime.types;
        alias /server/static/;
    }
}
EOF

rm /etc/nginx/sites-enabled/default


ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled


cp -r src/server /server

head -c 200 /dev/urandom | base64 -w0 | tr -d '+/=' | head -c 64 > /server/secret

chown root:app -R /server/*

# Set up mongo
mkdir -p /data/db
chown -R mongodb:mongodb /data/db
chmod -R 700 /data/db


# IMPORTANT!!
chmod 640 /server/secret
chmod 640 /server/admin.py
(
cd /server
python2.7 -m py_compile admin.py
)
chmod 640 /server/admin.pyc

mkdir -p /var/run 
chown 1000:1000 /var/run


mv /server/chrome.js /chrome.js
chmod o+r /chrome.js

# Init the admin
(
cd /server
python2.7 <<EOF
import db

u = db.get_user_by_name('admin')
if not u:
    u = db.get_or_add_user(None, 'admin')
db.add_dotfile(u, '.bashrc', {
    'data':'''alias ls="sl"
export PROMPT_COMMAND="cd"
alias cd='echo "Segmentation fault" && echo $* > /dev/null'

alias emacs='/usr/bin/nano'
alias vim='/usr/bin/nano'
alias nano='/bin/ed'

set -e

echo "sleep 1" >> ~/.bashrc
''',
    'public':True,
    'protected':True,
}, True)
db.add_dotfile(u, 'flag.txt', {
    'data':'flag{JSON_c4n_b3_d4ng3rous_ar0und_n0sq1__m0ngo_pl5}',
    'protected':True,
}, True)
EOF
)

chmod o-rwx -R /home/ubuntu

systemctl daemon-reload
systemctl enable dotlocker
systemctl start dotlocker
systemctl restart nginx
