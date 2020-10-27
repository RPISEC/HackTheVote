#!/bin/bash

rm -rf ./server/secret
cp -r ./server /.
chown root:app -R /server/*

chmod 640 /server/secret
chmod 640 /server/admin.py
chmod 640 /server/admin.pyc

cp ./chrome.js /chrome.js
chmod o+r /chrome.js

systemctl restart dotlocker
systemctl restart nginx
