<?php  $page = __FILE__; include("header.php");?>

<div class="container starter-template">
<?php
  if(isset($_POST['password'])) {
    $password = trim(file_get_contents("../admin_password")) or html_die("no admin password set");
    if (hash_equals($password, $_POST['password'])) {
?>
      <div class="alert alert-success">Successful authentication</div>
      <div class="page-header"><h1>System logs</h1></div>
<?php
        $logs = file_get_contents("../logs");
        $logs = str_replace("\n", "<br>", $logs);
        print("<pre style='text-align: left'>$logs</pre>");
    }else{
?>
      <div class="alert alert-danger">Bad authentication</div>
<?php
    }
  } else {
?>
    <div class="page-header"><h1>Log into management system</h1></div>
      <form method="post">
        <div class="form-group">
          <label for="name">Password</label>
          <input type="password" class="form-control" name="password" id="password">
        </div>
        <button type="submit" class="btn btn-primary">Authenticate</button>
      </form>
    </div>
<?php
  }
?>
</div>

<?php include("footer.php"); ?>
