<?php
session_start();
include "header.php";
if (isset($_GET['page']) && isset($_GET['key']) && is_string($_GET['page']) && is_string($_GET['key'])) {
    if (preg_match('/\\//',$_GET['page'])!==0) {
        //TODO Report to cyber police
        die("<b><font color=\"red\">You have been reported to the cyber police! Prepare to be locked up just like Hillary!</font></b>");
    }
    //var_dump(base64_encode(hash("sha1","secretkey".$_GET['page'],true)));
    if (base64_encode(hash("sha1","secretkey".$_GET['page'],true))!==$_GET['key']) {
        //TODO Report to cyber police
        die("<b><font color=\"red\">You have been reported to the cyber police! Prepare to be locked up just like Hillary!</font></b>");
    }
    $sql_conn = new mysqli('localhost','root',getenv('MYSQL_PASS'),'trump');

    if (isset($_POST['text']) && isset($_SESSION['id'])) {

        $stmt = $sql_conn->prepare("INSERT INTO comments (page,text,userId) VALUES (?,?,?)");
        if ($stmt == false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("ssi",$_GET['page'],$_POST['text'],$_SESSION['id']);
        $stmt->bind_result($text,$name,$image);
        $stmt->execute();
        $stmt->close();
    }


    echo "<div class=\"row\">";
    @readfile("./".$_GET['page']);

    $stmt = $sql_conn->prepare("SELECT comments.text,users.name,users.image FROM comments INNER JOIN users ON comments.userId=users.id WHERE comments.page=?");
    if ($stmt == false) {
        die($sql_conn->error);
    }
    $stmt->bind_param("s",$_GET['page']);
    $stmt->bind_result($text,$name,$image);
    $stmt->execute();
    if ($stmt->errno) {
        die($stmt->error);
    }
?>
<div class="panel panel-primary">
    <div class="panel-heading">
        <h3 class="panel-title">Comments</h3>
    </div>
    <div class="panel-body">
<?php
    while ($stmt->fetch()) {
?>
        <div class="row"><div class="col-sm-2">
            <p><img width=50 class="img-thumbnail" src="<?php echo htmlentities($image); ?>" /></p>
        </div><div class="col-md-10">
            <p><b><?php echo htmlentities($name); ?></b></p>
            <p><?php echo htmlentities($text) ?></p>
        </div></div>
<?php
    }
    $stmt->close();
    $sql_conn->close();
    if (isset($_SESSION['id'])) { ?>
        <div class="row"><div class="col-sm-12">
            <h4>Leave a comment</h4>
            <form action="watch.php?page=<?php echo htmlentities($_GET['page']); ?>&key=<?php echo htmlentities(urlencode($_GET['key']));?>" method="POST">
                <textarea class="form-control" rows=3 name="text"></textarea>
                <input class="btn btn-default" type="submit" name="comment" />
            </form>
        </div></div>
<?php } ?>
    </div>
</div>
<?php
} else { ?>
<h3>Trump Watch</h3>
<div class="list-group">
    
    <a class="list-group-item" href="watch.php?page=5&key=q3MNUno7lv3cvq50XwvBXoeK3Ho=">#DRAIN THE SWAMP</a>
    <a class="list-group-item" href="watch.php?page=4&key=ew5kR/1jBxH%2bSr8V%2b76ib0wxDC8=">First 100 Days (hint day #1 is LOCK HER UP)</a>
    <a class="list-group-item" href="watch.php?page=3&key=1HdLI2/HSmnhXUMzckYxCQWUBAc=">THEY HACKED US, WE MUST BE STRONG</a>
    <a class="list-group-item" href="watch.php?page=2&key=uTyPx54Qsfkg57qmTaaJw/0yCbs=">Trump wins everywhere!</a>
    <a class="list-group-item" href="watch.php?page=1&key=EdsTJgNT/MBp7ISvLSmDyubAkqg=">Even as a team they can't stump the trump!</a>
</div>
<?php }
include "footer.php";
?>

