<?php
session_start();

function isValid() 
{
    try {

        $url = 'https://www.google.com/recaptcha/api/siteverify';
        $data = ['secret'   => getenv("CAPTCHA_SECRET"),
                 'response' => $_POST['g-recaptcha-response'],
                 'remoteip' => $_SERVER['REMOTE_ADDR']];

        $options = [ 
            'http' => [
                'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
                'method'  => 'POST',
                'content' => http_build_query($data) 
            ]
        ];

        $context  = stream_context_create($options);
        $result = file_get_contents($url, false, $context);
        return json_decode($result)->success;
    }   
    catch (Exception $e) {
        return null;
    }   
}

function hex_dec($hex) {
    $dec = 0;
    $len = strlen($hex);
    for ($i = 1; $i <= $len; $i++)
        $dec = bcadd($dec, bcmul(strval(hexdec($hex[$i - 1])), bcpow(16, strval($len - $i))));
    
    return $dec;
}

function resetPassword(&$error, &$newPass) {

    if (isValid()!==True) {
        $error = "Invalid captcha";
        return false;
    } 

    if (!isset($_POST['user']) || !is_string($_POST['user'])) {
        $error = "No such user";
        return false;
    }

    if (!isset($_POST['entropy']) || !is_string($_POST['entropy'])) {
        $error = "No entropy";
        return false;
    } 
    
    if(!isset($_POST['pass']) || !is_string($_POST['pass'])) {
        $error = "No pass";
        return false;
    } 
    
    if (strlen($_POST['pass']) > 248) {
        $error = "Pass too long";
        return false;
    }

    $new = isset($_POST['new']);

    $sql_conn = new mysqli('localhost','root',getenv('MYSQL_PASS'),'trump');
    $stmt = $sql_conn->prepare("SELECT name FROM users WHERE name=?");
    if ($stmt == false) {
        die($sql_conn->error);
    }
    $stmt->bind_param("s",$_POST['user']);
    $stmt->bind_result($rUser);
    $stmt->execute();
    if ($stmt->errno) {
        die($stmt->error);
    }
    $stmt->fetch();
    $stmt->close();

    if (!$new) {
        if ($rUser !== $_POST['user']) {
            $error = "No such user";
            $sql_conn->close();
            return false;
        }
    } elseif ($rUser !== NULL) {
        $error = "Username taken.";
        $sql_conn->close();
        return false;
    }


    $entr = $_POST['entropy'];

    if ($entr > hex_dec('0x77359400')) {
        $error = "Entropy too low! Try again...";
        $sql_conn->close();
        return false;
    }

    $salt = mt_rand(1,intval($entr));
    
    if ($salt < hex_dec('0x10000000')) {
        $error = "Entropy too low! Try again...";
        $sql_conn->close();
        return false;
    }

    $salt = sprintf("%08x",$salt);
    $pass = $salt.$_POST['pass'];
    $pass = strrev($pass);
    $hash = hash("sha1",$pass,true);

    $newPass = base64_encode($hash);

    if ($new) {
        $stmt = $sql_conn->prepare("INSERT INTO users (name,oldPass) VALUES (?,?)");
        if ($stmt == false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("ss",$_POST['user'],$pass);
        $stmt->execute();
        if ($stmt->errno) {
            die($stmt->error);
        }
        $stmt->fetch();
        $stmt->close();
    } else {
        $stmt = $sql_conn->prepare("UPDATE users SET newPass=? WHERE name=?");
        if ($stmt == false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("ss",$pass,$_POST['user']);
        $stmt->execute();
        if ($stmt->errno) {
            die($stmt->error);
        }
        $stmt->fetch();
        $stmt->close();
    }

    $sql_conn->close();


    return True;
}

if (isset($_POST['reset']) || isset($_POST['new'])) {
    $page = 1;

    $new = isset($_POST['new']);
    $suc = resetPassword($error, $newPass);
} elseif (isset($_GET['confirm'])) {
    $page = 2;
    if (!isset($_SESSION['id'])) {
        header("Location: login.php");
        die();
    }
    $sql_conn = new mysqli('localhost','root',getenv('MYSQL_PASS'),'trump');
    $stmt = $sql_conn->prepare("UPDATE users SET oldPass=newPass, newPass=NULL WHERE id=?");
    if ($stmt == false) {
        die($sql_conn->error);
    }
    $stmt->bind_param("i",$_SESSION['id']);
    $stmt->execute();
    if ($stmt->errno) {
        die($stmt->error);
    }
    $stmt->close();
    $sql_conn->close();
} else {
    if (!isset($_SESSION['id'])) {
        header("Location: login.php");
        die();
    }
    $page = 0;
}

include "header.php";

if ($page == 2) {
    echo "<b>Your old password has been replaced</b>";
} elseif ($page == 1) {
    if ($suc) {
        if ($new) {
            echo "<b>Your account has been created, and your password is <code>$newPass</code></b>";
        } else {
            echo "<b>A new password has been generated. It will appear on your home page.</b>";
        }
    } else {
        if ($new) {
            include "register.php";
        } else {
            echo "<b><font color=\"red\">$error</font></b>";
        }
    }
} else { ?>
    <h3>Reset Password</h3>
    <form action="reset.php" method="POST">
        <div class="form-group">
            <label>New Password Seed</label>
            <input class="form-control" name="pass" />
            <script src='https://www.google.com/recaptcha/api.js'></script>
            <div class="g-recaptcha" data-sitekey="6LfZhAoUAAAAAOR5r9PwF6Xd1MKgq9A0DbXKd9ji"></div>
        </div>
        <input type="hidden" name="entropy" value="1073741824" />
        <input type="hidden" name="user" value="<?php echo $_SESSION['name']; ?>" />
        <input class="btn btn-default" type="submit" name="reset" value="reset" />
    </form>
<?php } 
include "footer.php"; ?>
