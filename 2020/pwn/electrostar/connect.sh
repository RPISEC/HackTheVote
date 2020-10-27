#!/bin/bash
#socat tcp:localhost:9000 FILE:`tty`,rawer,crnl,echo=0,icrnl=1,escape=0x03
socat tcp:3.81.25.197:9000 FILE:`tty`,rawer,echo=0,icrnl=1,escape=0x03
