<?php
error_reporting(E_ALL);
$hostPort = $_SERVER['HTTP_HOST'];
$hostPort = explode(":",$hostPort,2);
$host = $hostPort[0];
if (count($hostPort)>1)
    $port = ":".$hostPort[1];
else
    $port = "";
$path = $_SERVER['REQUEST_URI'];

if ($host==getenv("MAIN_DOMAIN")) {
    include_once("tld-site.php");
    die();
}
if ($host=="voteforme.".getenv("DOMAIN")) {
    include_once("pols-site.php");
    die();
}
if ($host=="polihosting.".getenv("DOMAIN")) {
    include_once("poli-index.php");
    die();
}
/*if (preg_match('/^000[a-f0-9]{8}\.chal.itszn.com/i',$host)==1) {
    include_once("pols-site.php");
    die();
}*/

if (preg_match("/^[a-zA-Z0-9]+.".getenv("DOMAIN")."$/i",$host)!==1) {
    http_response_code(404);
    $errorText = "We are not sure how you got to this page, but that is not a valid domain... Sorry...";
    include("tld-error.php");
    die("");
}

$ip = gethostbyname($host);

//TODO check for possible request from requested ip or some shit
if ($_SERVER['REMOTE_ADDR'] == getenv("PUBLIC_IP") || array_key_exists("X-".strtoupper(getenv("SITE_NAME"))."-PROXY-HOST", apache_request_headers())) {
    http_response_code(404);
    $errorText = "please no..";
    include("tld-error.php");
    die("");
}
if ($ip=="127.0.0.1" || $ip==getenv("PUBLIC_IP") || $ip=="0.0.0.0") {
    http_response_code(404);
    $errorText = "This domain has not been registered for a website yet. However that means it is avalible if you want it!";
    include("tld-error.php");
    die("");
}
$url = "http://$host";
$url = "https://$host";
$url = "https://$host$port$path";
#var_dump($url);
/*
if(isset($_SERVER['PHP_AUTH_USER'])) {
var_dump($_SERVER);
var_dump(apache_request_headers());
die();
}*/

$ch = curl_init($url);
$headers = array();
foreach (apache_request_headers() as $key => $value) {
    $headers[] = "$key: $value";
}
$headers["X-".strtoupper(getenv("SITE_NAME"))."-PROXY-HOST"] = $host;
if (isset($_SERVER['PHP_AUTH_USER']) && isset($_SERVER['PHP_AUTH_PW'])) {
    $headers[] = "Authorization: Basic ".base64_encode($_SERVER['PHP_AUTH_USER'].":".$_SERVER['PHP_AUTH_PW']);
}

#var_dump($headers);
#curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
#curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
curl_setopt($ch, CURLOPT_CAINFO, getenv("WEB_DIR")."/keys/CA.cert.pem");
curl_setopt($ch, CURLOPT_TIMEOUT, 1);

curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($_POST));
curl_setopt($ch, CURLOPT_HEADER, TRUE);  
curl_setopt($ch, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_0);

$data = curl_exec($ch);
if ($data===false) {
    http_response_code(500);
    $errno = curl_errno($ch);
    $errT = curl_error($ch); 
    if ($errno == 7)
        $errorText = "Our servers were unable to connect to the website. Try again later.";
    include("tld-error.php");
    die();
}
#var_dump($data);
list($headers, $body) = explode("\r\n\r\n", $data, 2);
$headers = explode("\r\n", $headers);
foreach ($headers as $header) {
    if (substr($header, 0, 15)!="Content-Length:")
        header($header);
}

echo $body;
#var_dump($headers);
?>
    <br/><img src="https://<?php echo getenv("MAIN_DOMAIN");?>/img/ad.png" height=50>
    <br/><small><a href="https://<?php echo getenv("MAIN_DOMAIN");?>">Powered by TLD</a></small>
