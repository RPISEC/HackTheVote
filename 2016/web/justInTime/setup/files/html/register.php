<?php  $page = __FILE__; include("header.php");?>

<div class="container starter-template">
<?php
  if (isset($_POST['name']) &&
      isset($_POST['affiliation']) &&
      isset($_POST['zip']) &&
      isset($_POST['address'])) {
    require_once("voter.php");
    $voter_id = generate_voter($_POST["name"], $_POST['address'], $_POST["affiliation"], $_POST["zip"]);
?>
    <div class="alert alert-success">You registered!</div>
    <div class="page-header"><h1>Voter ID</h1></div>
    <p>Bring a copy of this ID for election day.</p>
    <div class="well" style="overflow-wrap: break-word"><?= $voter_id ?></div>
    <p>You can confirm your ID is valid <a href="/check_reg.php?id=<?=$voter_id?>">here</a></p>

<?php
  } else {
?>
    <div class="page-header"><h1>Register to Vote!</h1></div>
      <form method="post">
        <div class="form-group">
          <label for="name">Your Name</label>
          <input type="Text" class="form-control" name="name" id="name" placeholder="John Smith">
        </div>
        <div class="form-group">
          <label for="name">Your Address</label>
          <input type="Text" class="form-control" name="address" id="address" placeholder="1 Main Street">
        </div>
        <div class="form-group">
          <label for="name">Your Zip Code</label>
          <input type="Text" class="form-control" name="zip" id="zip" placeholder="12345">
        </div>
        <div class="form-group">
          <label for="affiliation">Party Affiliation</label>
          <select class="form-control" id="affiliation" name="affiliation">
            <option>Independent</option>
            <option>Democrat</option>
            <option>Republican</option>
            <option>Libertarian</option>
            <option>Pirate</option>
            <option>None</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
<?php
  }
?>
</div>

<?php include("footer.php"); ?>
