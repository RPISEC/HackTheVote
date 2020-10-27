#!/bin/sh
# Path to  iodine executable
IOD="/usr/bin/iodine"

# top domain
IOTD="hillary.clinton.io"

# iodined server password
IOPASS="trumptrump"

# Device created by iodine
IODEV="dns0"

# The IP iodined server uses inside the tunnel
IOIP="10.0.0.1"

NS=`grep nameserver /etc/resolv.conf | head -1 | awk '{print $2}'`
GW=`netstat -rn | grep -v Gateway | grep G | awk '{print $2}' | head -1`
[ -z $IOPASS ] && echo "Enter your iodine password"
[ -z $IOPASS ] && $IOD -r $NS $IOTD
[ -n $IOPASS ] && $IOD -r -P "${IOPASS}" $NS $IOTD
if ps auxw | grep iodine | grep -v grep
then
    # route all traffic through iodine
    route del default
    route add $NS gw $GW
    route add default gw $IOIP $IODEV

    echo -e "Press enter when you are done with iodine\nand you want your routes back to normal"
    read
    kill -9 `ps auxw | grep iodine | grep -v grep | awk '{print $2}'`

    # restore routes
    route del default
    route delete $NS
    route add default gw $GW
else
    echo "there was a problem starting iodine"
    echo "try running it manually to troubleshoot"
fi
exit
