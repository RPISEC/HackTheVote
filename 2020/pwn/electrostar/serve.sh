#!/bin/bash
#timeout -sHUP -k1 120 stdbuf -i0 -o0 -e0 env -i /usr/bin/socat - "TCP-LISTEN:9000,reuseaddr,fork,exec:/bin/ls -li,pty,stderr,setsid,sigint,sighup,sane"
#/usr/bin/socat -d -d TCP-LISTEN:9000,reuseaddr,fork exec:"/bin/bash -li",pty,stderr,setsid,sigint,sighup,sane

cd bin

/usr/bin/socat -d -d -s TCP-LISTEN:9000,reuseaddr,fork EXEC:"env TERM=xterm-256color LD_LIBRARY_PATH=. timeout -sKILL 300 ./machine modules/init_module.img.sig",pty,stderr,setsid,sigint,sighup,echo=0,sane,raw,ignbrk=1
