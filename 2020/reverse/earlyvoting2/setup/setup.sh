#!/bin/bash

set -e

apt-get update -y
apt-get upgrade -y
apt-get install -y nginx python3-flask gunicorn

# Set up the user who will be running the app
groupadd -g 1337 app
useradd -g app -m -u 1337 app -s /bin/bash

cat > /etc/systemd/system/earlyvoting.service <<EOF
[Unit]
Description=earlyvoting
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/server
ExecStart=/usr/bin/stdbuf -o0 gunicorn -w 8 app:app -b unix:/tmp/gunicorn.sock --user app --access-logfile -
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
}
EOF

rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled

cp -r src/server /server

chown root:app -R /server/*

#chmod o-rwx -R /home/ubuntu

systemctl daemon-reload
systemctl enable earlyvoting
systemctl start earlyvoting
systemctl restart nginx
