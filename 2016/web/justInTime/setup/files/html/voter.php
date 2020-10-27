<?php

class Voter {
  var $name;
  var $addr;
  var $affil;
  var $zip;
  var $log;
  var $show_log = false;

  function Voter($name, $addr, $affil, $zip) {
    $this->name = $name;
    $this->addr = $addr;
    $this->affil = $affil;
    $this->zip = $zip;
    $this->log = "./data/$name/log";
  }

  function read_log() {
    if ($this->log && file_exists($this->log)) {
      return end(file($this->log));
    } else {
      return "File " . $this->log . " does not exist";
    }
  }

  function __toString() {
    $out = "Voter registration for {$this->name}:\n\tAddress: {$this->addr}" .
      "\n\tAffiliation: {$this->affil}\n\tZip: {$this->zip}";

    if ($this->show_log)
      $out .= "\n\nLast update to voter:\n" . $this->read_log();

    return $out;
  }
}

require_once("util.php");

function is_test_voter($name) {
  $f = "./data/$name/debug";
  if (file_exists($f)) {
    $debug_timestamp = file_get_contents($f);
    $debug_after = DateTime::createFromFormat('m/d/y H:i', $debug_timestamp);

    $now = new DateTime();
    if ($now >= $debug_after) {
      return True;
    }
  }
  return False;
}

function mark_test_voter($name, $raw_date=null) {
  $f = "./data/$name/debug";
  if (file_exists($f)) return;

  if (!isset($raw_date)) $raw_date = new DateTime();
  $date = $raw_date->format('m/d/y H:i');

  file_put_contents($f, $date) or die("Couldn't mark $name as test voter" . PHP_EOL);
  chmod($f, 0400);

  file_put_contents("./data/$name/log", "Marked $name as test voter at $date" . PHP_EOL, FILE_APPEND);
}

function create_voter_id($voter) {
  $vote_s = serialize($voter);
  $user_key = create_key($voter->name) or html_die("Couldn't create key for user - account already created <br>");

  $date = (new DateTime())->format('m/d/y H:i');
  file_put_contents($voter->log, "Registered {$voter->name} at $date" . PHP_EOL, FILE_APPEND) or html_die("Couldn't write to user log");

  $vote_s_sig = hash_hmac("sha512", $vote_s, $user_key);

  $system_key = get_system_key() or html_die("couldn't get system key");;
  $name_sig = hash_hmac("sha512", $voter->name, $system_key);

  return json_encode([$vote_s, $vote_s_sig, $voter->name, $name_sig]);
}

function generate_voter($name, $addr, $affil, $zip) {
  safe_string($name)  or html_die("Bad name");
  safe_string($addr)  or html_die("Bad address");
  safe_string($affil) or html_die("Bad affiliation");
  safe_string($zip)   or html_die("Bad zip");

  require_once("zip.php");
  $zip_int = intval($zip);
  in_array($zip_int, $zips) or html_die("Out of state zip");

  $v = new Voter($name, $addr, $affil, $zip);

  return base64_encode(create_voter_id($v));
}

function validate_voter($blob, $debug=False) {
  $unb64 = base64_decode($blob) or html_die("Could not decode base64");
  list($vote_s, $vote_s_sig, $name, $name_sig) = json_decode($unb64) or html_die("Could not decode json");

  $system_key = get_system_key();
  $valid_name_sig = hash_hmac("sha512", $name, $system_key);
  hash_equals($valid_name_sig, $name_sig) or html_die("Bad signature for name");

  $user_key = get_key($name);
  if (is_test_voter($name)) {
    html_die("$name is a testing account - it can't be used to vote");
  }
  if ($debug) {
    mark_test_voter($name);
    print("<pre>DEBUG: User signed with key " . base64_encode($user_key) . "</pre>");
  }

  $valid_vote_s_sig = hash_hmac("sha512", $vote_s, $user_key);
  hash_equals($valid_vote_s_sig, $vote_s_sig) or html_die("Bad signature for Voter object");

  $voter = unserialize($vote_s, ["Voter"]);
  return $voter;
}

?>
