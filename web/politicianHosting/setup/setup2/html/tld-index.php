<html>
<head>
<title><?php strtoupper(getenv("SITE_NAME")); ?></title>
    <script src="/js/jquery-2.1.4.min.js"></script>
    <script src="/js/bootstrap.min.js"></script>
    <link href="/css/flatly/bootstrap.min.css" rel="stylesheet"/>
</head>
<body>
<?php
    include("tld-header.php");
?>

<div class="container">
    <div class="row">
        <div class="panel panel-info">
            <div class="panel-heading">
                <h3 class="panel-title">What we do</h3>
            </div>
            <div class="panel-body">
                We provide proxy DNS as a service. You give us an IP and we give you a domain!
            </div>
        </div>
        <div class="panel panel-success">
            <div class="panel-heading">
                <h3 class="panel-title">
                <span class="glyphicon glyphicon-lock" aria-hidden="true"></span>
                End to End to End Encryption</h3>
            </div>
            <div class="panel-body">
                Our two step certificate system guarantees no one can spy on your traffic. <br/>
                <div class="row" style="text-align:center;">
                <div class="col-xs-2">
                    <h1><span class="glyphicon glyphicon-user"></span></h1>
                    <p>User</p>
                </div>
                <div class="col-xs-3">
                    <h1>
                        <span class="text-success">
                            <span class="glyphicon glyphicon-arrow-left"></span>
                            <span class="glyphicon glyphicon-lock"></span>
                            <span class="glyphicon glyphicon-arrow-right"></span>
                        </span>
                    </h1>
                    <p>Wildcard Certificate</p>
                </div>
                
                <div class="col-xs-2">
                    <h1><span class="glyphicon glyphicon-modal-window"></span></h1>
                    <p>Our Server</p>
                </div>
                <div class="col-xs-3">
                    <h1>
                        <span class="text-success">
                            <span class="glyphicon glyphicon-arrow-left"></span>
                            <span class="glyphicon glyphicon-lock"></span>
                            <span class="glyphicon glyphicon-arrow-right"></span>
                        </span>
                    </h1>
                    <p>Issued Certificate</p>
                </div>
                
                 
                <div class="col-xs-2">
                    <h1><span class="glyphicon glyphicon-globe"></span></h1>
                    <p>Web Site</p>
                </div>
                </div>
            </div>
        </div>
        <div class="panel panel-info">
            <div class="panel-heading">
                <h3 class="panel-title">Get started!</h3>
            </div>
            <div class="panel-body">
                <p><a href="/login">Create an account</a> to get one domain for free!</p>
                <p>Download our cert <a href="/CA.cert.pem" download>here.</a></p>
            </div>
        </div>
        <div class="panel panel-success">
            <div class="panel-heading">
                <h3 class="panel-title">FAQ</h3>
            </div>
            <div class="panel-body">
                <h4>How Do I Add A Domain</h4>
                <p>First you need to generate a CSR (Certificate Signing Request) for the subdomain of <code>.<?=getenv("DOMAIN");?></code>. Self-sign this request for now and set up your server to use it (or some other certificate doesn't matter at this step.)</p>
                <p>The <a href="/manage">Manage DNS</a> page will let you enter the desired subdomain, your server's ip, and the CSR request. It will also give you a token, which you need to put in <code>/dns_token</code> on your server. Once everything is in place hit submit to be added to the dns and to receive your signed certificate. Now switch your server to use that cert and everything should be golden!</p>

                <h4>What Are Error Domains</h4>
                <p>An error domain is some domain which you want to fall back on if there is a problem accessing any of your other domains. The error domain does not have to be one you own, but the owner will have to give permission to use it after you add it on the <a href="/manage">Manage DNS</a> page.</p>
                <p class="text-danger">Sorry, but error domains are termoraly diabled. You can still add them on the Manage DNS page, but your domains will not fall back to them at the moment...</p>
                
            </div>
        </div>
    </div>
</div>
    
</body>
</html>
