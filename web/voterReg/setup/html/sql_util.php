<?php
$sql_pass = getenv("MYSQL_PASS");

$sql_conn = new mysqli('localhost','root',$sql_pass,'votereg');
if ($sql_conn->connect_error) {
        die("SQL Connection Failed....");
}
?>
