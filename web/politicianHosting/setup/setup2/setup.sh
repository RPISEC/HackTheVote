#!/bin/bash

# YOU MUST CHANGE THIS BEFORE RUNNING THIS SCRIPT!!!
export WIN_IP=104.131.213.67

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

set -x

export DOMAIN=hosting.pwn.republican
export MYSQL_USER=root
export MYSQL_PASS=3eb7783af6e2353e634d0655d6bf1204a99241ff6e31b2f4ef4b10405759
export SITE_NAME=tld
export WEB_DIR=/var/www/$SITE_NAME
export MAIN_DOMAIN=$SITE_NAME.$DOMAIN
export LOC_IP=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
export PUBLIC_IP=$(dig +short myip.opendns.com @resolver1.opendns.com)


export DEBIAN_FRONTEND="noninteractive"
echo "mysql-server mysql-server/root_password password $MYSQL_PASS" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $MYSQL_PASS" | sudo debconf-set-selections


# Install dependences
apt-get update
apt-get install apache2 php mysql-server php-gd php-mysql curl php-curl libapache2-mod-php python -y

sh ./install_phantomjs.sh

mkdir /var/www/$SITE_NAME
cp -r * /var/www/$SITE_NAME
cd /var/www/$SITE_NAME

:<<COMMENT
# Create the root CA cert
openssl req -new -x509 -keyout keys/CA.key.pem -out keys/CA.cert.pem -days 3650 -nodes \
    -subj "/C=US/ST=DC/L=Washington/O=Sketchy Vote Getters/CN=$SITE_NAME.$DOMAIN"
cp keys/CA.cert.pem html/.

openssl req -new -keyout keys/$DOMAIN.key.pem -out keys/$DOMAIN.csr -nodes \
    -subj "/C=US/ST=DC/L=Washington/O=Sketchy Vote Getters/CN=*.$DOMAIN"

openssl x509 -req -days 3650 -in keys/$DOMAIN.csr \
    -CA keys/CA.cert.pem -CAkey keys/CA.key.pem -set_serial 01 > keys/$DOMAIN.cert.pem
cat keys/$DOMAIN.cert.pem keys/CA.cert.pem > keys/$DOMAIN.bun.pem
COMMENT

function rep {
    sed -i -- "s/MAIN_DOMAIN/$MAIN_DOMAIN/g" $1
    sed -i -- "s/DOMAIN/$DOMAIN/g" $1
    sed -i -- "s/WEB_DIR/\/var\/www\/$SITE_NAME/g" $1
    sed -i -- "s/LOC_IP/$LOC_IP/g" $1
}

rep bin/addDns.py
rep bin/generateCert.py
rep bin/phant/pol.js
rep mysql

cat mysql | mysql -u $MYSQL_USER -p$MYSQL_PASS 

cp keys/CA.cert.pem html/CA.cert.pem

chown root:root bin/addDns.py

chmod o+w keys/
touch bin/phant/log
chmod o+w bin/phant/log
chattr +ua bin/phant/log

cp /etc/hosts /etc/hosts.bk
chmod o+w /etc/hosts

cat >> /etc/hosts <<EOF

127.0.0.1 voteforme.$DOMAIN
127.0.0.1 $MAIN_DOMAIN

EOF

chattr +iu bin/addDns.py

cat > /etc/apache2/sites-enabled/000-default.conf <<EOF
<VirtualHost *:443>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/$SITE_NAME/html

    ErrorLog \${APACHE_LOG_DIR}/${SITE_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${SITE_NAME}_access.log combined

    SSLCertificateFile /var/www/$SITE_NAME/keys/$DOMAIN.cert.pem
    SSLCertificateKeyFile /var/www/$SITE_NAME/keys/$DOMAIN.key.pem
    SSLCertificateChainFile /var/www/$SITE_NAME/keys/$DOMAIN.bun.pem

    SetEnv MYSQL_USER $MYSQL_USER
    SetEnv MYSQL_PASS $MYSQL_PASS
    SetEnv DOMAIN $DOMAIN
    SetEnv SITE_NAME $SITE_NAME
    SetEnv MAIN_DOMAIN $SITE_NAME.$DOMAIN
    SetEnv WEB_DIR $WEB_DIR
    SetEnv PUBLIC_IP $PUBLIC_IP
    SetEnv WIN_IP $WIN_IP

    <Directory "/var/www/$SITE_NAME/html">
        Options -Indexes
        RewriteEngine on
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule . index.php [L]
    </Directory>

</VirtualHost>
EOF

cat > /etc/apache2/ports.conf <<EOF

<IfModule ssl_module>
        Listen 443
</IfModule>

<IfModule mod_gnutls.c>
        Listen 443
</IfModule>

EOF




sudo a2enmod ssl
sudo a2enmod rewrite
service apache2 restart

    


