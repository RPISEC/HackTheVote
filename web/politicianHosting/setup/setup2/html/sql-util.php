<?php
$sql_pass = getenv("MYSQL_PASS");

$sql_conn = new mysqli('localhost',getenv("MYSQL_USER"),$sql_pass,'voteforme');
if ($sql_conn->connect_error) {
    die("SQL Connection Failed....");
}
?>
