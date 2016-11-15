<?php  $page = __FILE__; include("header.php");?>

<div class="container starter-template">
<?php
  if(isset($_POST['id'])) { 
    require_once("voter.php");
    $debug = isset($_GET['debugpw']) && strcmp($_GET['debugpw'], "thebluegrassstate") !== false;
    $voter_info = validate_voter($_POST['id'], $debug);
    $voter_info = str_replace("\n", "<br>", $voter_info);
?>
    <div class="panel panel-info">
      <div class="panel-heading"><h3 class="panel-title">Valid Voter ID</h3></div>
      <div class="panel-body"><?= $voter_info ?></div>
    </div>
<?php
  } else {
?>
    <div class="page-header"><h1>Validate your Voter ID</h1></div>
      <form method=POST>
        <div class="form-group">
          <label for="id">ID</label>
          <textarea rows="5" class="form-control" name="id" id="id" required><?php if (isset($_GET['id'])) print($_GET['id']); ?></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Check</button>
      </form>
    </div>
<?php
  }
?>
</div>

<?php include("footer.php"); ?>
