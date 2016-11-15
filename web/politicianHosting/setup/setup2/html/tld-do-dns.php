<?php

$name = $_POST['name'].".".getenv("DOMAIN");

include("sql-util.php");
$st = $sql_conn->prepare("SELECT userid,locked from dns where name=?;"); 
if ($st===false) 
    die($sql_conn->error);
$st->bind_param("s",$name);
$st->execute();
$st->store_result();

$dnsGood = true;
$dnsUpdate = false;
//var_dump($st);

if ($st->num_rows!==0) {
    $dnsUpdate = true;
    $st->bind_result($owner,$locked);
    $st->fetch();
    if ($owner!=$_SESSION['user']) {
       $dnsGood = false; 
       $error = "Sorry you do not own that name.";
    } elseif ($locked!=0) {
       $dnsGood = false; 
       $error = "Sorry this domain is locked and cannot be changed.";
    }
} else {
    $st->close();
    $st = $sql_conn->prepare("SELECT name from dns where userid=?;"); 
    if ($st===false) 
        die($sql_conn->error);
    $st->bind_param("i",$_SESSION['user']);
    $st->execute();
    $st->store_result();

    $dnsGood = true;

    if ($st->num_rows>0) {
        $dnsGood = false;
        $error = "Sorry, you have exceeded the number of free domains you can make. You can still edit ones you own though.";
    }
}
$st->close();

if ($dnsGood) {


    //$_SESSION['dns_token']="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    exec("python ".getenv("WEB_DIR")."/bin/generateCert.py ".escapeshellarg($_POST['ip'])." 443 ".escapeshellarg($_SESSION['dns_token'])." ".escapeshellarg($name)." ".escapeshellarg($_POST['csr']),$cert, $exitval);

    if ($exitval==1) {
        $error = "Well you messed something up with your cert stuff.";
    } elseif ($exitval==2) {
        $error = "Failed to make request to your ip. Please make sure you are using ssl. (We want everything to be super secure)";
    } elseif ($exitval==3) {
        $error = "The data we got back from your server did not match the token we were expecting! Here have a new one and try again.";
    } elseif ($exitval==4) {
        $error = "The CSR you provided was somehow invalid... Please try again...";
    } elseif ($exitval==5) {
        $error = "The common name on the CSR did not match the one we expected. What are you trying to do here???";
    } elseif ($exitval==6) {
        $error = "The name you provided was invalid, please try again...";
    } else {
        $subject = array_shift($cert);
        $cert = implode("\n",$cert);
        exec("python ".getenv("WEB_DIR")."/bin/addDns.py ".escapeshellarg($name)." ".escapeshellarg($_POST['ip']),$execout,$exitval);
        if ($exitval==1) {
            $error = "Well you messed something up.";
        } elseif ($exitval==2) {
            $error = "Really now? How did you manage to mess the name up like this";
        } elseif ($exitval==3) {
            $error = "Really now? How did you manage to mess the ip up like this";
        } else {
            $didDns = true;
            if ($dnsUpdate) {
                $st = $sql_conn->prepare("UPDATE dns SET ip=?, subject=? WHERE name=?;"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("sss",$_POST['ip'],$subject,$name);
            } else {
                $st = $sql_conn->prepare("INSERT INTO dns (userid,name,ip,subject) VALUES (?,?,?,?);"); 
                if ($st===false) 
                    die($sql_conn->error);
                $st->bind_param("isss",$_SESSION['user'],$name,$_POST['ip'],$subject);
            }
            $st->execute();
            $st->close();
        }

    }
}
$sql_conn->close();
//var_dump($error);
//var_dump($cert);

//die();
