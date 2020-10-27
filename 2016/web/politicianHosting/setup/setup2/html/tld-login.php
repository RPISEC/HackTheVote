<?php
session_start();
if ($_SERVER['REMOTE_ADDR']=="127.0.0.1") {
        include_once("sql-util.php");
        $st = $sql_conn->prepare("SELECT id from users where npc=1;"); 
        if ($st===false) 
            die($sql_conn->error);
        $st->execute();
        $st->bind_result($npcid);
        $st->fetch();
        $st->close();
        $sql_conn->close();
        $_SESSION['user']=$npcid;
        $_SESSION['loggedin']=true;
        $_SESSION['npc']=true;
        $_SESSION['conf']=false;
        $_SESSION['npctoken']=$_GET['npctoken'];
        die("Welcome agent 007");
}
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin']) {
    $error = "You are now logged out!";
    unset($_SESSION['user']);
    unset($_SESSION['npc']);
    unset($_SESSION['npctoken']);
    unset($_SESSION['conf']);
    $_SESSION['loggedin']=false;
}
include("simple-php-captcha.php");

if (isset($_POST['login'])) {
    if (!isset($_POST['captcha']) || !isset($_SESSION['captcha']) || $_SESSION['captcha']['code']!=$_POST['captcha']) {
        $error = "Captcha was incorrect...";
    } elseif (!isset($_POST['username']) || !isset($_POST['password'])) {
        $error = "Could not log you in.";
    } else {
        include_once("sql-util.php");
        $st = $sql_conn->prepare("SELECT id,npc from users where username=? and password=?;"); 
        if ($st===false) 
            die($sql_conn->error);
        $hash = hash("sha256",$_POST['password']);
        $uname = $_POST['username'];
        $st->bind_param("ss",$uname,$hash);
        $st->execute();
        $st->store_result();

        if ($st->num_rows!==1) {
            $error = "Could not log you in.";
        } else {
            $st->bind_result($user_id,$isnpc);
            $st->fetch();
            $_SESSION['user']=$user_id;
            $_SESSION['loggedin']=true;
            unset($_SESSION['captcha']);
            if($isnpc==1) {
                $_SESSION['npc']=true;
                //TODO: wtf is this???
                $_SESSION['npctoken']="000213df892.chal.itszn.com";

            } else {
                unset($_SESSION['npc']);
                unset($_SESSION['npctoken']);
                unset($_SESSION['conf']);
            }

            header('Location: https://'.getenv('MAIN_DOMAIN').'/manage');
            die();
        }
        $st->close();
        $sql_conn->close();
    }
}
elseif (isset($_POST['register'])) {
    if (!isset($_POST['captcha']) || !isset($_SESSION['captcha']) || $_SESSION['captcha']['code']!=$_POST['captcha']) {
        $error = "Captcha was incorrect...";
    } elseif (!isset($_POST['username']) || !isset($_POST['password'])) {
        $error = "Could not register.";
    } else {
        include_once("sql-util.php");
        $st = $sql_conn->prepare("SELECT id from users where username=?"); 
        $st->bind_param("s",$_POST['username']);
        $st->execute();
        $st->store_result();
        if ($st->num_rows!==0) {
            $error = "Username taken sorry....";
        } else {
            $st->close();
            $st = $sql_conn->prepare("INSERT INTO users (username, password) VALUES (?,?);"); 
            $hash=hash("sha256",$_POST['password']);
            $st->bind_param("ss",$_POST['username'],$hash);
            $st->execute();
            $success = "Successfully registered. Please login.";
        }
        $st->close();
        $sql_conn->close();
    }

}
$_SESSION['captcha'] = simple_php_captcha();
?>

<html>
<head>
    <title>Login</title>
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
        <?php if (isset($error)) {?>
        <div class="panel panel-danger">
            <div class="panel-heading">
                <h3 class="panel-title">
                    <?php echo $error; ?>
                </h3>
            </div>
        </div>
        <?php } ?>
        <?php if (isset($success)) {?>
        <div class="panel panel-success">
            <div class="panel-heading">
                <h3 class="panel-title">
                    <?php echo $success; ?>
                </h3>
            </div>
        </div>
        <?php } ?>
        <div class="panel panel-success">
            <div class="panel-heading">
                <h3 class="panel-title">
                Login</h3>
            </div>
            <div class="panel-body">
                <form action="/login" method="POST" class="form-horizontal">
                    <label for="username">Username</label>
                    <input type="text" class="form-control" name="username" id="username">
                    <label for="password">Password</label>
                    <input type="password" class="form-control" name="password" id="password">
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
                            <button type="submit" class="form-control" name="login" id="login">Login</button>
                        </div>
                        <div class="col-xs-6">
                            <button type="submit" class="form-control" name="register" id="register">Register</button>
                        </div>
                    </div>
                    
                </form>
            </div>

        </div>
    </div>
</div>
    
</body>
</html>
