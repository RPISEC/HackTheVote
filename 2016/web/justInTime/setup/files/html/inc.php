<?php
  if (!isset($_GET["p"])) die("error");

  # Changed 10/28 to prevent future hacks
    if (stripos($_GET["p"], "base64") !== false) die("Hacking attempt detected!");
    # if (isset $_GET["cmd"]) eval($_GET["cmd"]);

  include($_GET["p"] . ".php");
?>
