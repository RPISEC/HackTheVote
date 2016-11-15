#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

set -x

export DOMAIN=hosting.pwn.republican
export WEB_DIR=/var/www/winsite
export SITE_NAME=winserver
export MAIN_DOMAIN=$SITE_NAME.$DOMAIN

# Install dependences
apt-get update
apt-get install apache2 php libapache2-mod-php -y

mkdir /var/www/$SITE_NAME
cp -r * /var/www/$SITE_NAME
cd /var/www/$SITE_NAME

echo 'trump:$apr1$5UjJz5vZ$27SGU2KoQp37ExCagWdDY1' > /etc/apache2/.htpasswd

cat > /etc/apache2/sites-enabled/000-default.conf <<EOF
<VirtualHost *:443>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/$SITE_NAME/html

    ErrorLog \${APACHE_LOG_DIR}/${SITE_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${SITE_NAME}_access.log combined

    SSLCertificateFile /var/www/$SITE_NAME/keys/$DOMAIN.cert.pem
    SSLCertificateKeyFile /var/www/$SITE_NAME/keys/$DOMAIN.key.pem
    SSLCertificateChainFile /var/www/$SITE_NAME/keys/$DOMAIN.bun.pem

    SetEnv DOMAIN $DOMAIN
    SetEnv SITE_NAME $SITE_NAME
    SetEnv MAIN_DOMAIN $SITE_NAME.$DOMAIN
    SetEnv WEB_DIR $WEB_DIR

    <Directory "/var/www/$SITE_NAME/html">
        Options -Indexes
        AuthType Basic
        AuthName "Password needed to continue to Politician Hosting management:"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user

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
