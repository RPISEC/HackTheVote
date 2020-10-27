<?php
session_start();
if (!isset($_SESSION['loggedin']) || !$_SESSION['loggedin']) {
    header('Location: https://'.getenv("MAIN_DOMAIN").'/login');
    die();
}
if (isset($_SESSION['npc']) && $_SESSION['npc'] && $_SERVER['REMOTE_ADDR']!="127.0.0.1" && (!isset($_SESSION['conf']) || !$_SESSION['conf'])) {
    $error = false;
    $good = false;
    if (isset($_POST['confirm']) && isset($_POST['email'])) {
        if ($_POST['email'] != "Sup3r_P4k_d0L13rs@polihost.".getenv("DOMAIN")) {
            $error=true;
        } else {
            $good=true;
            $_SESSION['conf'] = true;
            unset($error);
        }
    }
    if (!$good) {
        if ($error) {
            header('Location: https://'.getenv("MAIN_DOMAIN").'/login');
            die();
        } ?>
<html>
<head>
    <title>Confirm your identity</title>
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
                <h3 class="panel-title">Confirm your identity</h3>
            </div>
            <div class="panel-body">
                <p>Your IP Address suddenly changed, so we need to confirm you are really you.</p>
                <p>Enter the email address you used on the CSR of <code>voteforme.<?=getenv("DOMAIN");?></code>.</p>
                <p>If it is incorrect, you will be logged out! So make sure to type carefully, case matters!</p>
                <form action="/manage" method="POST">
                    <div class="form-group">
                        <label for="email">Email used on the CSR of <code>voteforme.<?=getenv("DOMAIN");?></code>:</label>
                        <input type="email" class="form-control" id="email" name="email" placeholder="Email">
                    </div>
                    <button type="submit" name="confirm" class="btn btn-success btn-lg">Confirm</button>
                </form>
            </div>
        </div>
    </div>
</div>
</body>
</html>
<?php
        die(); 
    }
}
if (isset($_POST['create'])) {
    if (!isset($_POST['captcha']) || !isset($_SESSION['captcha']) || $_SESSION['captcha']['code']!=$_POST['captcha']) {
        $error = "Captcha was incorrect...";
    } elseif (!isset($_POST['name']) || !isset($_POST['ip']) || !isset($_POST['csr']) || !isset($_SESSION['dns_token'])) {
        $error = "Some fields where missing";
    } else {
        include("tld-do-dns.php");
    }
//    unset($_SESSION['captcha']);

}
elseif (isset($_POST['adderror'])) {
    if (!isset($_POST['errorname'])) {
        $eeror = "Missing the domain name to set";
    } else {
        include("sql-util.php");
        $st = $sql_conn->prepare("select id,userid from dns where name=?"); 
        if ($st===false) 
            die($sql_conn->error);
        $name = $_POST['errorname'].".".getenv("DOMAIN");
        $st->bind_param("s",$name);
        $st->execute();
        $st->store_result();
        if ($st->num_rows===0) {
            $eerror="That name does not exist.";
        } else {
            $st->bind_result($domainid,$owner);
            $st->fetch();
            $st->close();
            if ($owner!=$_SESSION['user']) {
                $valid = 0;
                $esuccess="Domain was set, but the owner will have to confirm it first.";
            } else {
                $valid = 1;
                $esuccess="Domain was set.";
            }
            if (!isset($_SESSION['npc']) || !$_SESSION['npc']) {
                $st = $sql_conn->prepare("update users set errorid=?,erroraccepted=? where id=?"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("iii",$domainid,$valid,$_SESSION['user']);
            } else {
                $st = $sql_conn->prepare("update npc set errorid=?,erroraccepted=? where token=?"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("iis",$domainid,$valid,$_SESSION['npctoken']);
            }
            $st->execute();
        }
        $st->close();
        $sql_conn->close();
    }
}
elseif (isset($_POST['allow'])) {
    if (isset($_POST['name']) && isset($_POST['userid'])) {
            //    echo "<script>alert('".$_POST['name']."')</script>";
            //    echo "<script>alert('".$_POST['userid']."')</script>";
        include("sql-util.php");
        $st = $sql_conn->prepare("select id from dns where name=? and userid=?"); 
        if ($st===false) 
            die($sql_conn->error);
        $st->bind_param("si",$_POST['name'],$_SESSION['user']);
        $st->execute();
        $st->store_result();
        if ($st->num_rows!==0) {
            //echo "<script>alert('found!')</script>";
            $st->bind_result($dnsid);

            $st->fetch();
            //echo "<script>alert('".$dnsid."')</script>";
            $st->close();
            $st = $sql_conn->prepare("select npc from users where id=? and npc=1"); 
            if ($st===false) 
                die($sql_conn->error);
            $st->bind_param("i",$_POST['userid']);
            $st->execute();
            $st->store_result();
            if ($st->num_rows!==0) {
                $st->close();
                $st = $sql_conn->prepare("update npc set erroraccepted=1 where ip=? and errorid=?"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("si",$_SERVER['REMOTE_ADDR'],$dnsid);
            } else {
                $st->close();
                $st = $sql_conn->prepare("update users set erroraccepted=1 where id=? and errorid=?"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("ii",$_POST['userid'],$dnsid);
            }
            $st->execute();
        }
        $st->close();
        $sql_conn->close();
        
    }
}
include("simple-php-captcha.php");
$_SESSION['captcha'] = simple_php_captcha();
$_SESSION['dns_token'] = hash("md5",strval(mt_rand()));
?>

<html>
<head>
    <title>Manage DNS</title>
    <script src="/js/jquery-2.1.4.min.js"></script>
    <script src="/js/bootstrap.min.js"></script>
    <link href="/css/flatly/bootstrap.min.css" rel="stylesheet"/>
</head>
<body>
<?php
        
    include("tld-header.php");
    include("tld-manage-util.php");
?>

<div class="container">
    <div class="row">
        <div class="panel panel-info">
            <div class="panel-heading">
                <h3 class="panel-title">Your DNS</h3>
                <!-- USER ID = <?=$_SESSION['user']?> -->
            </div>
            <div class="panel-body">
            <table class="table table-condensed">
            <?php
                include("sql-util.php");
                if (!isset($_SESSION['npc']) || !$_SESSION['npc']) {
                    $st = $sql_conn->prepare("SELECT id,name,ip,subject,locked from dns where userid=?;"); 
                    if ($st===false) 
                        die($sql_conn->error);
                    $st->bind_param("i",$_SESSION['user']);
                } else {
                    $st = $sql_conn->prepare("(SELECT id,name,ip,subject,locked from dns where name=?) union (SELECT id,name,ip,subject,locked from dns where name='voteforme.".getenv("DOMAIN")."')"); 
                    if ($st===false) 
                        die($sql_conn->error);
                    $st->bind_param("s",$_SESSION['npctoken']);
                }
                $st->execute();
                $st->store_result();
                
                if ($st->num_rows===0) {
                    echo '<tr class="danger"><td>You have no DNS entries...</td></tr>';
                } else {
                    $st->bind_result($dnsid,$dnsName,$ip,$subject,$locked);
                    for ($i=0;$i<$st->num_rows;$i++) {
                        $st->fetch();
                        /*echo "<pre>";
                        var_dump($subject);
                        echo "</pre>";*/

                        showDnsEntry($dnsName, $ip, $subject,$locked);
                        if (!isset($_SESSION['npc']) || $_SESSION['npc']===false) {
                            $st2 = $sql_conn->prepare("(SELECT id,username from users where errorid=? and erroraccepted=0) union (select id,username from users where npc=1 and (select 1 from npc where errorid=? and erroraccepted=0))"); 
                            if ($st2===false) 
                                die($sql_conn->error);
                            $st2->bind_param("ii",$dnsid,$dnsid);
                            $st2->execute();
                            $st2->store_result();
                            
                            if ($st2->num_rows!==0) {
                                $st2->bind_result($userid,$username);
                                for ($j=0; $j<$st2->num_rows;$j++) {
                                    $st2->fetch(); ?>

                                    <tr><td><div class="col-xs-6">
                                    <?php echo htmlentities($username); ?> wants to use this as an error server.
                                    </div>

                                    <div class="col-xs-2">
                                        <form action="/manage" method="POST">
                                        <input type="hidden" name="name" value="<?php echo htmlentities($dnsName); ?>">
                                        <input type="hidden" name="userid" value="<?php echo htmlentities($userid); ?>">
                                        <button type="submit" class="btn btn-primary btn-sm" name="allow">Allow them</button>
                                        </form>
                                    </div>
                                    </td></tr>
                                    <?php
                                }
                            }
                            $st2->close();
                        }
                    }
                    $st->close();
                    if (!isset($_SESSION['npc']) || $_SESSION['npc']===false) {
                        $st = $sql_conn->prepare("SELECT name,ip,subject from dns where id=(select errorid from users where id=? and erroraccepted=1) LIMIT 1;"); 
                        if ($st===false) 
                            die($sql_conn->error);
                        $st->bind_param("i",$_SESSION['user']);
                    } else { 
                        $st = $sql_conn->prepare("SELECT name,ip,subject from dns where id=(select errorid from npc where token=? and erroraccepted=1) LIMIT 1;"); 
                        if ($st===false) 
                            die($sql_conn->error);
                        $st->bind_param("s",$_SESSION['npctoken']);
                    }
                    $st->execute();
                    $st->store_result();
                    //var_dump($st);
                    
                    if ($st->num_rows===0) {
                        echo '<tr class="warning"><td>You have no server to fall back on for errors. If you requested one, the owner must confirm it first.</td></tr>';
                    } else {
                        $st->bind_result($dnsName,$ip,$subject);
                        $st->fetch();
                        showDnsEntry("Error Domain: ".$dnsName, $ip, $subject, false);
                    } ?>
                    <tr><td></td></tr>
                    <tr class="info"><td>Set Error Server</td></tr>
                    <?php if (isset($eerror)) { ?>
                    <tr><td></td></tr>
                    <tr class="danger"><td><?php echo $eerror; ?></td></tr>
                    <?php } ?>
                    <?php if (isset($esuccess)) { ?>
                    <tr><td></td></tr>
                    <tr class="success"><td><?php echo $esuccess; ?></td></tr>
                    <?php } ?>
                    <tr><td>
                    <form action="/manage" method="POST" class="form-inline">
                        <div class="form-group">
                        <label for="errorname">Error Domain</label>
                        <div class="input-group">
                            <input type="text" class="form-control" name="errorname" id="errorname" describedby="errortld">
                            <span class="input-group-addon" id="errortld">.<?=getenv("DOMAIN");?></span>
                        </div>
                        <button type="submit" class="btn btn-primary" name="adderror">Set Server</button> 
                        </div>
                    </form>
                    </td></tr>
                    <?php

                }


                $st->close();
                $sql_conn->close();
            ?>
            </table>
            </div>
        </div>
        <?php if (isset($error)) {?>
        <div class="panel panel-danger">
            <div class="panel-heading">
                <h3 class="panel-title">
                    <?php echo $error; ?>
                </h3>
            </div>
        </div>
        <?php } ?>
        <div class="panel panel-success">
            <div class="panel-heading">
                <h3 class="panel-title">
                Add or Edit a DNS entry</h3>
            </div>
            <div class="panel-body">
                <?php if (!isset($didDns) || !$didDns) { ?>
                <div class="panel panel-warning">
                    <div class="panel-body">
                        <p>To authenticate your server, have it return this token for a request to <code>/dns_token</code></p>
                        <code><?php echo $_SESSION['dns_token']; ?></code>
                    </div>
                </div>
                <form action="/manage" method="POST" class="form-horizontal">
                    <label for="name">Domain Name (Enter one you own to change it)</label>
                    <div class="input-group">
                        <!--div class="col-xs-12"-->
                            <input type="text" class="form-control" name="name" id="name" describedby="tld">
                            <span class="input-group-addon" id="tld">.<?=getenv("DOMAIN");?></span>
                        <!--/div-->
                    </div>
                    <label for="ip">IP Address</label>
                    <input type="text" class="form-control" name="ip" id="ip">
                    <label for="ip">CSR Request</label>
                    <textarea type="text" class="form-control" name="csr" id="csr"></textarea>
                    <label for="captcha">Captcha</label><br/>
                    <div class="form-group">
                        <div class="col-xs-2">
                            <img src="<?php echo $_SESSION['captcha']['image_src'];?>" class="img-thumbnail"/>
                        </div>
                        <div class="col-xs-10">
                            <input type="text" class="form-control" name="captcha" id="captcha">
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="col-xs-6">
                            <button type="submit" class="form-control" name="create" id="create">Create DNS Record</button>
                        </div>
                    </div>
                    
                </form>
                <?php } else { ?>
                            <p>Successfully added the dns entry. Below if your certificate.</p>
                <code><pre><?php echo htmlentities($cert); ?></pre></code>
                <?php } ?>
                    
                
                
            </div>
        </div>
    </div>
</div>
    
</body>
</html>
