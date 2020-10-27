<?php $page = __FILE__; include("header.php");?>

<div class="container">
  <div class="starter-template">
    <div class="jumbotron">
      <h2>Welcome to <?= $STATE ?>'s new online voter registration system!</h2>
      <p>To prevent voter fraud, residents must use this system to register to vote</p>
    </div>
    <div class="row">
      <div class ="col-md-6">
        <div class="page-header"><h1>How it works</h1></div>
        <ol class="list-group">
          <li class="list-group-item">Fill out your voter information</li>
          <li class="list-group-item">Recieve your digital <em>VoterID</em></li>
          <li class="list-group-item">Bring your <em>VoterID</em> with you on voting day</li>
        </ol>
      </div>
      <div class ="col-md-6">
        <div class="page-header"><h1>When it works</h1></div>
        <ol class="list-group">
          <li class="list-group-item">24 hours a day</li>
          <li class="list-group-item">7 days a week</li>
          <li class="list-group-item">Until registration closes at 6am November 6</li>
        </ol>
      </div>
    </div>
  </div>
</div>

<?php include("footer.php"); ?>
