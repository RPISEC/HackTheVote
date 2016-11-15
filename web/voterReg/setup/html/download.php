<?php
header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Transfer-Encoding: binary');

chdir('downloads');
if (!isset($_GET['dl'])) {
    die("Filename missing");
}
$dl = $_GET['dl'].'.pdf';
if (!file_exists($dl)) {
    http_response_code(404);
    echo "File ".htmlentities($dl." doesn't exist. Please report the error to the sysadmin...");
}
@readfile($dl);

