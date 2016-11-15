<html>
  <head>
    <script> setTimeout(function() { location.reload(); }, 10000); </script>
  </head>
<?php
require_once("util.php");
$now = time();
if ($has_ended) {
  print("<div style=\"text-align: center\">Registration is closed</div>");
}else{
  $delta = date_diff(new DateTime(), $end);
  print($delta->format("<div style=\"text-align: center\">%d days, %h hours, and %i minutes until registration closes</div>"));
}
?>
</html>
