<?php
// mysql -u root -p < database.sql
session_start();

if (!isset($_SESSION['id'])) {
    header('Location: login.php');
    die();
}

$sql_conn = new mysqli('localhost','root',getenv('MYSQL_PASS'),'trump');
$stmt = $sql_conn->prepare("SELECT name, newPass, image FROM users WHERE id=?");
if ($stmt == false) {
    die($sql_conn->error);
}
$stmt->bind_param("i",$_SESSION['id']);
$stmt->bind_result($name,$newPass,$img);
$stmt->execute();
$stmt->fetch();
if ($stmt->errno) {
    die($stmt->error);
}
$stmt->close();
$sql_conn->close();

include "header.php";
?>
<div class="row">
<h3>Trump Watch</h3>
<p>A site to share the activities of our future God-Emperor Donald J Trump.</p>
</div>

<div class="row">
    <div class="panel panel-success">
    <div class="panel-heading">
        <h3 class="panel-title">Your Profile</h4>
    </div>
    <div class="panel-body">
        <div class="row">
            <div class="col-sm-3">
                <img width=100 class="img-thumbnail" src="<?php echo htmlentities($img); ?>" /><br/>
            </div>
            <div class="col-md-9">
            Logged in as <b><?php echo htmlentities($name); ?></b><br/>
            
<?php if ($newPass!=NULL) { ?>
            <b>Your password was changed to <code>
<?php 
    $hash = hash("sha1",$newPass,true);
    echo base64_encode($hash);
?>
            </code><br/>
            Click <a href="reset.php?confirm">here</a> to confirm and overwrite your old password.</b>
<?php 
} 
if ($_SESSION['id']===1) {
    echo "<p>Hello admin, your flag is <code>".getenv('FLAG')."</code></p>";
}
?>
            </div>
        </div>
    </div>
    </div>
</div>
<?php include "footer.php"; ?>
