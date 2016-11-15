#!/bin/sh

apt-get update
apt-get install apache2 php libapache2-mod-php

timedatectl set-timezone America/New_York

cat > /etc/apache2/sites-enabled/000-default.conf <<EOF
<VirtualHost *:80>
    DocumentRoot /var/www/html

    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined

    <Directory "/var/www/html">
        Options -Indexes
    </Directory>
    <Directory "/var/www/html/data">
        Options -Indexes
        Order deny,allow
        Deny from all
    </Directory>
</VirtualHost>
EOF

service apache2 restart

rm -f /var/www/html/index.html
cp -r files/* /var/www/.
chmod o+w /var/www/html/data
chown root:root -R /var/www
