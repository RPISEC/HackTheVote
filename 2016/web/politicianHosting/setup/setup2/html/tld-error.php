<html>
<head>
    <title>Error</title>
    <script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <!--link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet"/-->
    <link href="https://bootswatch.com/flatly/bootstrap.min.css" rel="stylesheet"/>
</head>
<body>
<?php
    $page = "/error";
    include("tld-header.php");
?>

<div class="container">
    <div class="row">
        <div class="panel panel-danger">
            <div class="panel-heading">
                <h3 class="panel-title">Oh No! There was a problem...</h3>
            </div>
            <div class="panel-body">
                <?php
                    if (isset($errorText)) {
                        echo "<p>".$errorText."</p>";
                    } else {
                        echo "<p>Something went wrong connecting you to this page, and we don't know what! ";
                        echo "You should try and contact the owner of the page to get them to fix it.</p>";
                    }
                    if (isset($errT) && isset($errno)) {
                        echo "<p>Error Details:</p><code>Error Number ".$errno.": ".htmlentities($errT)."</code>";
                    }
                ?>
            </div>
        </div>
    </div>
</div>
    
</body>
</html>
