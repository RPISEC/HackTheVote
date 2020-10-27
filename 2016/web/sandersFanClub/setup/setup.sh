#!/bin/sh

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install nginx
sudo cp nginx-SandersFanClub.conf /etc/nginx/sites-enabled/
sudo cp -r webroot/ /var/www/sanders/
sudo nginx -t
sudo nginx -s reload
