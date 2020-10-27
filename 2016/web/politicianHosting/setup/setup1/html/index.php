<?php
//#p<T?p8DH*]^@fZ9e.5=M&s%Be[qnq=J
//super_secret_documents_for_2016_race

$files = array("super_secret_documents_for_2016_race");
$secret_files = array("goverment_secrets_TOP_SECRET_dont_tell_anyone.txt","campaign_plans.txt",
    "champagne_plans.txt","is_the_government_spying_on_citizens.txt");

if (isset($_GET['p'])) {
    $path = explode("/",$_GET['p']);
    if (count($path)>0 && $path[0]=="")
        array_shift($path);
    if (count($path)>1) {
        if ($path[0]!="super_secret_documents_for_2016_race") {
            $error = true;
            $path = array();
        } else {
            if ($path[1]=="") {
                $path = array("super_secret_documents_for_2016_race");
                $directory = true;
            } else if (!in_array($path[1],$secret_files,true)) {
                $path = array("super_secret_documents_for_2016_race");
                $error = true;
            } else {
                $file = $path[1];
            }
        }
    } elseif (count($path)==1) {
        if ($path[0]=="super_secret_documents_for_2016_race") {
            $directory = true;
        } else if (!in_array($path[0],$files,true)) {
            $path = array();
            $error = true;
        } else {
            $file = $path[0];
        }
    } else {
        $directory = true;
    }

} else {
    $path = array();
    $directory = true;
}
?>
<html>
<head>
    <title>Politician Hosting</title>
    <script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <link href="/css/bootstrap.min.css" rel="stylesheet"/>
</head>
<body>
<div class="container">
    <div class="row">
        <h3>Politician Hosting</h3>
        <ul class="breadcrumb">
            <li <?php if (!isset($path) || count($path)==0) { echo 'class="active"'; }?>>
            <a href="/">Website</a></li>
<?php 
    if (isset($path)) {
        for ($i=0; $i<count($path); $i++) { ?>
            <li <?php if ($i==count($path)) { echo 'class="active"'; }?>>
            <a href="/?p=<?php echo htmlentities(implode("/",array_slice($path,0,$i+1)));?>">
            <?php echo htmlentities($path[$i]);?></a></li>
<?php   }
} ?>
        </ul>
    </div>
    <div class="row">
<?php if (isset($error) && $error) { ?>
        <div class="alert alert-danger">
            <strong>404 Not Found</strong>
        </div>
<?php } 
if (isset($directory) && $directory) {
    if (count($path)==0)
        $dirfs = $files;
    else 
        $dirfs = $secret_files;
?>
        <table class="table table-hover">
            <thead>
            <tr><th>Directory</th><tr>
            </thead>
            <tbody>
<?php
    for ($i=0; $i<count($dirfs); $i++) {
?>
            <tr><td>
            <a href="/?p=<?php echo htmlentities(implode("/",$path)."/".$dirfs[$i]);?>">
            <?php echo htmlentities($dirfs[$i]); ?></a>
            </td></tr>
<?php } ?>
            </tbody>
        </table>
<?php } 
if (isset($file) && $file) {
?>
        <!--div class="well"--><pre>
<?php if (count($path)==1) {
} else {
    if ($path[1]=="goverment_secrets_TOP_SECRET_dont_tell_anyone.txt") {
        echo "The flag is flag{Bu7_1_Th0gh7_H77PS_w4s_S3cure}";
    } elseif ($path[1]=="campaign_plans.txt") {
        echo "1. Steal people's hearts\n2. Steal people's souls\n3. Steal election";
    } elseif ($path[1]=="champagne_plans.txt") {
        echo "1. Drink\n2. ???\n3. Win election";
    } elseif ($path[1]=="is_the_government_spying_on_citizens.txt") {
        echo "yes";
    }
}

?>
        </pre><!--/div-->
<?php } ?>
    </div>
</div>


</body>
</html>
