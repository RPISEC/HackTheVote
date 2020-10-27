<?php
include_once "header.php";
?>
    <h3>Register</h3>
<?php if (isset($error)) {
    echo "<b><font color=\"red\">$error</font></b>";
} ?>
    <form action="reset.php" method="POST">
        <div class="form-group">
            <label>Username</label>
            <input class="form-control" name="user" />
        </div>
        <div class="form-group">
            <label>Password Seed</label>
            <input class="form-control" type="password" name="pass" />
        </div>
        <script src='https://www.google.com/recaptcha/api.js'></script>
        <div class="g-recaptcha" data-sitekey="6LfZhAoUAAAAAOR5r9PwF6Xd1MKgq9A0DbXKd9ji"></div>
        <input type="hidden" name="entropy" value="1073741824" />
        <input class="btn btn-default" type="submit" name="new" />
    </form>
<?php
include_once "footer.php";
?>
    
