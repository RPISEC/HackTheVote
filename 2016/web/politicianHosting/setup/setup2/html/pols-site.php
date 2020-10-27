<?php
    $page = "/";
    if (isset($_SERVER['REQUEST_URI'])) {
        $page = $_SERVER["REQUEST_URI"];
        $page = explode("?",$page);
        $page = array_shift($page);
    }
    if ($page == "/")
        include("pols-index.php");
    elseif ($page == "/simple-php-captcha.php") {
        include("tld-error.php");

        //include("simple-php-captcha.php");
    } elseif ($page == "/about")
        include("pols-about.php");
    elseif ($page == "/comment")
        include("pols-comment.php");
    else {
        http_response_code(404);
        echo "<html><head><title>404</title></head><body><h1>404 Not Found</h1></body></html>";
    }
?>
    <br/><small><a href="https://polihosting.<?php echo getenv("DOMAIN");?>">Hosted by Politician Hosting</a></small>
<br/><small><a href="https://<?php echo getenv("MAIN_DOMAIN");?>">Powered by TLD</a></small>
