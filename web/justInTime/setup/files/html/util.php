<?php
date_default_timezone_set('America/New_York');

function menu_link($page, $path, $name) {
  if ($page == $path || ($page == "/" && $path == "index.php")) {
    return "<li class=\"active\"><a href=\"#\">$name</a></li>";
  } else {
    return "<li><a href=\"$path\">$name</a></li>";
  }
}

function html_die($msg) {
  die("<div class=\"alert alert-danger\" role=\"alert\">Error: $msg</div>");
}

function safe_string($s) {
  # Spaces/alphanumeric and under 20 chars
  if (strlen($s) > 20) return False;
  return ctype_alnum(str_replace(" ","", $s));
}

function create_key($user) {
  $dir = "./data/$user/";
  $f = "$dir/key";

  if (file_exists($f)) {
    return False;
  }

  if (file_exists($dir) == false) {
    mkdir($dir, 0700, true) or die("Couldn't create data directory for $user");
  }

  $key = openssl_random_pseudo_bytes(64);
  file_put_contents($f, $key) or die("Couldn't save key");
  chmod($f, 0400);
  return $key;
}

function get_key($user) {
  $dir = "./data/$user/";
  $f = "$dir/key";
  if (file_exists($f)) {
    $key = file_get_contents($f);
    return $key;
  }
  return False;
}

function get_system_key() {
  $f = "../system_key";
  if (file_exists($f)) {
    $key = file_get_contents($f);
  } else {
    $key = openssl_random_pseudo_bytes(64);
    file_put_contents($f, $key) or die("Couldn't save system key");
  }
  return $key;
}

require_once("vars.php");
?>
