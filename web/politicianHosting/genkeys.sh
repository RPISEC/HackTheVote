#!/bin/bash

export DOMAIN=hosting.pwn.republican
export MYSQL_USER=root
export MYSQL_PASS=mysql_pass
export SITE_NAME=tld
export WEB_DIR=/var/www/$SITE_NAME
export MAIN_DOMAIN=$SITE_NAME.$DOMAIN
export LOC_IP=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
export REMOTE_IP=54.236.213.11

export WIN_IP=104.131.213.67

# Create the root CA cert
openssl req -new -x509 -keyout keys/CA.key.pem -out keys/CA.cert.pem -days 3650 -nodes \
    -subj "/C=US/ST=DC/L=Washington/O=Sketchy Vote Getters/CN=$SITE_NAME.$DOMAIN"
cp keys/CA.cert.pem html/.

openssl req -new -keyout keys/$DOMAIN.key.pem -out keys/$DOMAIN.csr -nodes \
    -subj "/C=US/ST=DC/L=Washington/O=Sketchy Vote Getters/CN=*.$DOMAIN"

openssl x509 -req -days 3650 -in keys/$DOMAIN.csr \
    -CA keys/CA.cert.pem -CAkey keys/CA.key.pem -set_serial 01 > keys/$DOMAIN.cert.pem
cat keys/$DOMAIN.cert.pem keys/CA.cert.pem > keys/$DOMAIN.bun.pem
