#!/bin/bash

# Torque needs to write files
chmod -R 700 .
# But make sure it can't overwrite anything important
find . -type f -exec chmod 400 "{}" \;
# But also we need to run the game
chmod +x ./Torque\ Demo\ Debug\ OSX.app/Contents/MacOS/Torque\ Demo\ Debug\ OSX start.sh
chmod 600 console.log
chmod -R 500 starter.web/public

./Torque\ Demo\ Debug\ OSX.app/Contents/MacOS/Torque\ Demo\ Debug\ OSX -mod starter.fps -dedicated -mod starter.web -listen 28080 -mission starter.fps/data/missions/stronghold.mis
