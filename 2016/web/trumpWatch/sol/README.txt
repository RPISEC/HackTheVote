This challenge uses a combination of edgecases in PHP and MYSQL.

- First see that the blog pages seem to have a page name and key
    http://watch.pwn.republican/watch.php?page=1&key=EdsTJgNT/MBp7ISvLSmDyubAkqg=
- Decoding the base64 you get raw bytes of 11db13260353fcc069ec84af2d2983cae6c092a8
- Googling that hash reveals it is 'secretkey1', so the key must be sha1('secretkey' + page)
- You can now read files, but not use the / character, so you are restricted to the html directory
    ie: http://watch.pwn.republican/watch.php?page=reset.php&key=sSiPIS98RY/X9JQ2G1uEhcqq0I4=
- Reading the php source for reset you see the main bugs
- The strange "entropy" parameter in the request generating a salt

    $entr = $_POST['entropy'];

    if ($entr > hex_dec('0x77359400')) {
        $error = "Entropy too low! Try again...";
        $sql_conn->close();
        return false;
    }

    $salt = mt_rand(1,intval($entr));

    if ($salt < hex_dec('0x10000000')) {
        $error = "Entropy too low! Try again...";
        $sql_conn->close();
        return false;
    }

    o The bug here is a edge case of mt_rand.
        mt_rand only generates up 32 random bits, so if the difference between min and max is > 0xffffffff, mt_rand will pad the number to the appropriate number of bits.
        Setting max to PHP_INT_MAX (a 64 bit number) will make the lower 32 bits = 1
            php > printf("%x\n",mt_rand(1,PHP_INT_MAX));
            59d7e31f00000001
    o However to ge allowed to set a value above 0x77359400 we need to bypass that check.
    o Looking at hex_dec:
        function hex_dec($hex) {
            $dec = 0;
            $len = strlen($hex);
            for ($i = 1; $i <= $len; $i++)
                $dec = bcadd($dec, bcmul(strval(hexdec($hex[$i - 1])), bcpow(16, strval($len - $i))));
            
            return $dec;
        }
    o It uses the php big number library. This library stores all of its numbers in strings, so the final $dec will be a string.
    o To cause $entr > '2000000000' to be false, we need to have $entr not be cast to a number in the compare, or both values will be cast to numbers.
    o Do something like adding a non numeric character to the end such as 'X'
    o We need to find the a large signed (2**n)-1 that starts with a 1 in decimal form
        (I just went with 0xfffffffffffffff, but 0x1fffffffffffffff should work)
        Note this will leave us with 7 zeros, and then 8 random nibbles and then a 0 nible, such as 0x0a4f8cd94000001
    o Now we have '1152921504606846975X' > '2000000000' which is false since '1' < '2'
    o Luckily intval will stop at the X, and still return PHP_INT_MAX
- The second bug is with MYSQL varchar truncation
    o In /database.sql we find this table defintion:
        CREATE TABLE users (
            id int NOT NULL AUTO_INCREMENT key,
            name varchar(256) NOT NULL UNIQUE,
            oldPass varchar(256) NOT NULL,
            newPass varchar(256) DEFAULT NULL,
            image varchar(256) NOT NULL DEFAULT "https://i.imgur.com/C35yeEC.jpg"
        );
    o We see that the newPass column is 256 bytes long.
    o Looking at the rest of the reset code:
        if (strlen($_POST['pass']) > 248) {
            $error = "Pass too long";
            return false;
        }
        ...
        $salt = sprintf("%08x",$salt);
        $pass = $salt.$_POST['pass'];
        $pass = strrev($pass);
        $hash = hash("sha1",$pass,true);
        ...
        $stmt = $sql_conn->prepare("UPDATE users SET newPass=? WHERE name=?");
        if ($stmt == false) {
            die($sql_conn->error);
        }
        $stmt->bind_param("ss",$pass,$_POST['user']);
        $stmt->execute();
    o The pass param is limited to 248 bytes, and with what appears to be 8 more bytes, it wouldn't truncate, but %08x actually writes 16, putting it at 264 bytes.
    o The salt is prepended, but the string is revered. This means the 0s from before are in the first 8 nibbles, and the 7 random nibbles are truncated when stored into the database. One nibble remains after the 0s, so there are 16 possible passwords.
- Now the login page:
        function hashPass($pass) {
            $hash = hash("sha1",$pass,true);
            return base64_encode($hash);
        }
        ...
        } elseif (hashPass($oldPass)===$_POST['pass'] || ($newPass != NULL && hashPass($newPass)===$_POST['pass'])) {
        ...
    o It hashes both the old and replaced passwords and checks to see if you submitted either, and if so logs you in
    o So just sha1 the 16 possible passes, and one will log you in as admin.
- Once logged in, the flag is on the index.





    

    

    

