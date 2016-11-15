<?php
    $page = "/";
    if (isset($_SERVER['REQUEST_URI'])) {
        $page = $_SERVER["REQUEST_URI"];
        $token = "?";
        $page = explode($token,$page);
        $page = array_shift($page);
    }
    if ($page == "/")
        include("tld-index.php");
    elseif ($page == "/simple-php-captcha.php") {
        include("tld-error.php");

        //include("simple-php-captcha.php");
    } elseif ($page == "/manage")
        include("tld-manage.php");
    elseif ($page == "/login")
        include("tld-login.php");
    else {
        http_response_code(404);
        $errorText = "<h4>404</h4>The page you were looking for could not be found...";
        include("tld-error.php");
    }

?>
