#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

set -x

export MYSQL_USER=root
export MYSQL_PASS=4fc7ab6f3de3fe8645cd99859e1473af1d8e56c87a8b2dc19ff4f28d9017

export DEBIAN_FRONTEND="noninteractive"
echo "mysql-server mysql-server/root_password password $MYSQL_PASS" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $MYSQL_PASS" | sudo debconf-set-selections

apt-get update
apt-get install apache2 php mysql-server php-mysql libapache2-mod-php -y

mkdir /var/www/html
rm /var/www/html/index.html

cp -r html/* /var/www/html/.

cat mysql | mysql -u $MYSQL_USER -p$MYSQL_PASS

chmod -R go-r /etc/apache2

chmod -R go-w /var/www/html

cat > /etc/apache2/sites-enabled/000-default.conf <<EOF
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    ErrorLog \${APACHE_LOG_DIR}/reg_error.log
    CustomLog \${APACHE_LOG_DIR}/reg_access.log combined

    SetEnv MYSQL_USER $MYSQL_USER
    SetEnv MYSQL_PASS $MYSQL_PASS

    <Directory "/var/www/html">
        Options -Indexes
    </Directory>
    <Directory "/var/www/html/secure">
        Options +Indexes
    </Directory>

</VirtualHost>
EOF

service apache2 restart
