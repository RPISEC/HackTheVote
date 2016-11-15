<html>
<head>
    <title>Send Me Money... I mean a message...</title>
    <script src="/js/jquery-2.1.4.min.js"></script>
    <script src="/js/bootstrap.min.js"></script>
    <link href="/css/paper/bootstrap.min.css" rel="stylesheet"/>
</head>
<body style='background-image: url("https://i.imgur.com/FlSjKHB.png");'>
<?php
    include("pols-header.php");
?>

<div class="container" >
<?php 
    $isnpc = false;
    if ($_SERVER['REMOTE_ADDR']=="::1" || $_SERVER['REMOTE_ADDR']=="127.0.0.1") {
        $isnpc = true;
        if(isset($_GET['session'])) {
            session_id($_GET['session']);
            session_start();
            if (isset($_GET['done'])) {
                $ip = $_SESSION['lastip'];
                include_once("sql-util.php");
                $st = $sql_conn->prepare("UPDATE npc set cooldown=0 where ip=?;"); 
                $st->bind_param("s",$ip);
                $st->execute();
                $st->close();
                $sql_conn->close();
                die("Well played, well played...");
            }
            $_POST['email'] = $_SESSION['email'];
            $_POST['message'] = $_SESSION['message'];
            $_POST['preview'] = true;
        }
        else {
            session_start();
        }
        
    } else {
        session_start();
    }

    
    include("simple-php-captcha.php");
    if ((isset($_POST['send']) || isset($_POST['preview'])) && isset($_POST['email']) && isset($_POST['message'])) {
        $shouldshow = false;
        if (isset($_POST['preview'])) {
            $shouldshow = true;
        }
        elseif (!isset($_POST['captcha']) || !isset($_SESSION['captcha']) || $_SESSION['captcha']['code']!=$_POST['captcha']) {
            $error = "Captcha was incorrect!";
        } elseif(!$isnpc) { 
            //Get or create ip token
            //var_dump($_SERVER['REMOTE_ADDR']);

            include_once("sql-util.php");
            $st = $sql_conn->prepare("SELECT token,cooldown from npc where ip=?"); 
            $st->bind_param("s",$_SERVER['REMOTE_ADDR']);
            $st->execute();
            $st->store_result();
            $cooldown = 0;
            if ($st->num_rows==0) {
                $token = "000".substr(hash("md5",strval(mt_rand())),0,8).".".getenv("DOMAIN");
                $st->close();
                $st = $sql_conn->prepare("INSERT into npc (ip,token,cooldown) values (?,?,1);"); 
                $st->bind_param("ss",$_SERVER['REMOTE_ADDR'],$token);
                $st->execute();

                $st->close();
                $st = $sql_conn->prepare("INSERT into dns (userid,name,ip,subject) values ((select id from users where npc=1 limit 1),?,'".getenv("WIN_IP")."',?)");
                $subject = '{"C": "aa", "CN": "*.'.getenv("DOMAIN").'", "L": "aa", "O": "Politician Hosting", "ST": "aa", "OU": "Politician Hosting", "subject": "","emailAddress": "login@polihost.'.getenv("DOMAIN").'"}';
                $st->bind_param("ss",$token,$subject);
                $st->execute();
                exec("python ".getenv("WEB_DIR")."/bin/addDns.py ".escapeshellarg($token)." ".escapeshellarg(getenv("WIN_IP")),$execout,$exitval);
                //var_dump($execout);
            } else {
                $st->bind_result($token,$cooldown);
                $st->fetch();
                if ($cooldown===0) {
                    $st->close();
                    $st = $sql_conn->prepare("UPDATE npc set cooldown=1 where ip=?;"); 
                    $st->bind_param("s",$_SERVER['REMOTE_ADDR']);
                    $st->execute();
                }
            }
            //var_dump($cooldown);
            $st->close();
            $sql_conn->close();
            if ($cooldown!=0) {
                $error = "Whoa! You are sending me messages too fast, slow down a bit...";
            } else {
                //var_dump($token);
                
                $_SESSION['lastip'] = $_SERVER['REMOTE_ADDR'];
                $_SESSION['email'] = $_POST['email'];
                $_SESSION['message'] = $_POST['message'];
                //Start the bot
                $shouldshow = true;
                exec("/usr/local/bin/phantomjs --ignore-ssl-errors=true ".getenv("WEB_DIR")."/bin/phant/pol.js ".escapeshellarg(session_id())." ".escapeshellarg($token)." >> ".getenv("WEB_DIR")."/bin/phant/log 2>> ".getenv("WEB_DIR")."/bin/phant/log &");
                //exec("/usr/local/bin/phantomjs --ignore-ssl-errors=true /var/www/chals/voteforme/phant/pol.js ".escapeshellarg(session_id())." &", $output);
                //var_dump($output);
            }
        }
        if ($shouldshow) {

?>
    <div class="row">
        <div class="panel panel-primary">
            <div class="panel-heading">
                <?php if (isset($_POST['send'])) {?>
                <h3 class="panel-title">Message sent! Here is how I will see your message once I log in and look at it</h3>
                <?php } else { ?>
                <h3 class="panel-title">Here is a preview of how I will see your message</h3>
                <?php } ?>
            </div>
        </div>
    </div>
    <div class="panel panel-primary">
        <div class="panel-body">

            <div class="col-xs-12">
                <?php echo "<b>".$_POST['email'].":</b><br/>".$_POST['message']; ?>
            </div>
        </div>
    </div>

<?php
        }
    }

    if ($_SERVER['REMOTE_ADDR']!="::1" && $_SERVER['REMOTE_ADDR']!="127.0.0.1") {
        $_SESSION['captcha'] = simple_php_captcha();
    }
?>
    <div class="row">
        <div class="panel panel-danger">
            <div class="panel-heading">
                <h3 class="panel-title">Send me a message about how you are going to <b>VOTE FOR ME</b></h3>
            </div>
        </div>
    </div>
    <div class="panel panel-primary">
        <div class="panel-body">

            <div class="col-xs-12">
                <form action="/comment" method="POST" class="form-horizontal">
                    <fieldset>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" class="form-control" id="email" name="email" placeholder="Email">
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea class="form-control" rows="5" name="message" id="message" placeholder="I'm going to vote for YOU!"></textarea>
                    </div>
                    <label for="captcha">Captcha</label><br/>
                    <div class="form-group">
                        <div class="col-xs-2">
                            <img src="<?php echo $_SESSION['captcha']['image_src'];?>" class="img-thumbnail"/>
                        </div>
                        <div class="col-xs-10">
                            <input type="text" class="form-control" name="captcha" id="captcha" placeholder="Are you a robot?">
                        </div>
                    </div>
                    <?php if (isset($error)) { ?>
                    <p class="bg-warning"><?php echo $error; ?></p>
                    <?php } ?>
                    <button type="submit" name="preview" class="btn btn-danger btn-lg">Preview</button>
                    <button type="submit" name="send" class="btn btn-primary btn-lg">Send Me A Message</button>
                    </fieldset>
                </form>
            </div>
        </div>
    </div>
</div>
    
</body>
</html>
