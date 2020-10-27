#!/bin/bash

if [ "$(id -u)" -ne "0" ] ; then
    echo "please run as root / with sudo"
    exit
fi

set -exo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install xinetd gdb python3 -y

# if the binaries need to be changed, simply replacing them in /
# should do, xinetd simply exec's whatever is at /wrapper at the time
cp src/wrapper src/fileshare src/cleaner.py src/flag /
chown root:root /wrapper /fileshare /cleaner.py /flag
chmod o-rwx src setup
mv /flag /flag-$(head -c 32 /dev/urandom | sha256sum | cut -d ' ' -f1)
tar czhf /libs.tar.gz /lib/x86_64-linux-gnu/libc.so.6 /lib64/ld-linux-x86-64.so.2 /lib/x86_64-linux-gnu/libpthread.so.0 /lib64/ld-linux-x86-64.so.2 /bin/sh

cat > /run.sh <<EOF
#!/bin/sh
exec timeout -s 9 120 /wrapper
EOF
chmod +x /run.sh

cat > /etc/xinetd.d/fileshare <<EOF
service fileshare
{
    disable = no
    type = UNLISTED
    wait = no
    server = /run.sh
    socket_type = stream
    protocol = tcp
    user = root
    port = 1717
    flags = REUSE
    rlimit_as = 128M
    per_source = 5
}
EOF

# if machine gets rebooted, will need to re-run these
setsid python3 /cleaner.py &
service xinetd stop
setsid xinetd -dontfork &
