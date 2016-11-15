<?php function showDnsEntry($dnsName,$ip,$subject,$locked) {
    $subject = json_decode($subject,true);
    ?>
        <tr class="success"><td><b>
        <?php echo htmlentities($dnsName);
            if ($locked!=0) {
                echo ' <span class="glyphicon glyphicon-lock"></span>';  
            }
        ?>
        </b></td></tr>
        <tr><td>
        <div class="col-xs-12">
        <b>IP:</b> <?php echo htmlentities($ip); ?>
        </div>
        </td></tr>
        <tr><td>
        <div class="col-xs-12"><b>Certificate Info:</b></div>
        <?php if ($subject==null) {
            echo "Sorry could not load certificate info...";
        } else {
            if (isset($subject['CN'])) { ?>
        <div class="col-xs-3">
        Common Name:
        <input class="form-control input-sm" type="text" value="<?php echo $subject['CN']; ?>" readonly>
        </div>
        <?php }
            if (isset($subject['O'])) { ?>
        <div class="col-xs-3">
        Organization:
        <input class="form-control input-sm" type="text" value="<?php echo $subject['O']; ?>" readonly>
        </div>
        <?php }
            if (isset($subject['OU'])) { ?>
        <div class="col-xs-3">
        Organizational Unit:
        <input class="form-control input-sm" type="text" value="<?php echo $subject['OU']; ?>" readonly>
        </div>
        <?php }
            if (isset($subject['emailAddress'])) { ?>
        <div class="col-xs-3">
        Email:
        <input class="form-control input-sm" type="text" value="<?php echo $subject['emailAddress']; ?>" readonly>
        </div>
        <?php }
        }?>
        </td></tr>
    <?php
}
