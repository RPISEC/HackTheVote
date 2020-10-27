<?php
session_start();

function hashPass($pass) {
    $hash = hash("sha1",$pass,true);
    return base64_encode($hash);
}

$error = NULL;
if (isset($_POST['login']) && isset($_POST['user']) && isset($_POST['pass'])) {
    $sql_conn = new mysqli('localhost','root',getenv('MYSQL_PASS'),'trump');
    $stmt = $sql_conn->prepare("SELECT id, oldPass, newPass FROM users WHERE name=?");
    if ($stmt == false) {
        die($sql_conn->error);
    }
    $stmt->bind_param("s",$_POST['user']);
    $stmt->bind_result($uid,$oldPass,$newPass);
    $stmt->execute();
    $stmt->fetch();
    if ($stmt->errno) {
        die($stmt->error);
    }
    $stmt->close();
    $sql_conn->close();

    if ($oldPass==NULL) {
        $error = "Could not log you in.";
    } elseif (hashPass($oldPass)===$_POST['pass'] || ($newPass != NULL && hashPass($newPass)===$_POST['pass'])) {
        $_SESSION['id'] = $uid;
        $_SESSION['name'] = $_POST['user'];
        header('Location: index.php');
        die();
    } else {
        $error = "Could not log you in.";
    }
}

include "header.php";
if ($error != NULL) { ?>
    <h3>Login</h3>
    <b><font color="red"><?php echo $error; ?></font></b>
<?php } ?>
    <h3>Login</h3>
    <form action="login.php" method="POST">
        <div class="form-group">
        <label>Username</label>
        <input class="form-control" name="user" />
        </div>
        <div class="form-group">
        <label>Password</label>
        <input class="form-control" type="password" name="pass" />
        </div>
        <input class="btn btn-default" type="submit" name="login" />
    </form>
<?php include "footer.php"; ?>
