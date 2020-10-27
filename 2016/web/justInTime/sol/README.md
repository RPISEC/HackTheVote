Just in Time
=============
300 point  
Web  
Andrew Fasano  

TL;DR;
-------------------
This challenge can be solved by exploiting the time change from EDT to EST that will happen on Nov 6.  

1. Prior to the change, teams should be able to obtain the source code through a local-file inclusion vulnerability
1. With the source code, teams should be able to learn of the `d3bug` parameter on the verify page
1. Teams need to create an account and verify it with that parameter sometime in the hour between 1AM EDT and 1AM EST
1. After the time change, teams need to create a modified Voter object and sign it with the key provided previously
1. A malformed voter object can be used to lead the `admin_password` file which can then be used to log into the management site
1. The flag is printed in the (short) logs on the management page as the only RSA fingerprint that successfully authenticated


After the time change is over (2am EST 11/6), the challenge cannot be solved by the intended solution and will disable itself so nobody wastes more time.


Bug 1: Local File Inclusion to get PHP source
---------------------------
The countdown timer shown is an iframe pointing to the page `inc.php` which calls PHP's `include()` on whatever argument it gets in the `p` parameter. This can be used to read the source code of any file ends in `.php` with php filters by requesting pages such as:
```
/inc.php?p=php://filter/string.rot13/resource=index
```

The commonly-used filter `php://filter/convert.base64-encode/resource=` is blocked by throwing an error if the given parameter contains the string `base64`.

With the source code, you can find that the site prints extra information when the  `d3bug` parameter is set to `1337` on the verify page.

VoterIDs and User Keys
----------------------
When a user creates a VotingID, a `Voter` object is created, and then returned to them in the following format:  
```
base64_encode(json.dumps([Serialize(VoterObject), sign(Serialize(VoterObject), userkey), username, sign(username, private_server_key)]))
```
The userkey is just 64 random bytes, written into the file "./data/`username`/key"  

When this string is sent to the verify page, the signatures are validated. First the site ensures that the username was correctly signed by the `private_server_key`. If the username is correctly signed, the site loads the file "./data/`username`/key" to check if the `VoterObject` field is correctly signed. If so, it unserializes the object.


Debug User Accounts
------------------
When the `debugpw` parameter is set to `thebluegrassstate` on the verify page, the VotingID for a name will be marked as `debug` by writing the current time into "./data/`username`/debug". After the account is marked as such, the page will print out `base64encode(userkey)` and then `unserialize(VoterObject)`.

When a VotingID is given to the verify page, it checks if a debug file exists for the given name. If it exists, the timestamp in that file is compared to the current date. If the debug file's timestamp is earlier than the current time, an error message will be printed and execution will stop before the call to `unserialize`

BUG 2: Timezone Logic
---------------------------
Background information: Until 11/6 at 2am, we're in Eastern Daylight Time (EDT). After 1:59:59AM the timezone changes to Eastern Standard Time (EST) and the time then changes to 1:00:00AM.  

A VotingID can be validated (with `d3bug` set) on 11/6 1:30AM EDT and that will reveal the userkey object and mark that username's VotingID as being invalid after `11/6 1:30`. But after the timezone change, the time (without a timezone) will be `11/6 1:00` which is earlier than the time written to the debug file. At this point, you can construct a new `Voter` Object, and sign it using the previously leaked key. `unserialize()` will be called on this object if it is signed correctly.

BUG 3: Unserialize malicious objects
-----------------------------------
Once you can create an arbitrary `Voter` object that the server will `unserialize`, you just need to make one with the `log` property equal to `../admin_password` and `show_log` to `1`. When the server prints this object on the validate page, it will print the contents of the `admin_password` file.

An example of such object is:
```
O:5:"Voter":6:{s:4:"name";s:6:"andrew";s:4:"addr";s:4:"addr";s:5:"affil";s:3:"dem";s:3:"zip";i:12345;s:3:"log";s:17:"../admin_password";s:8:"show_log";b:1;}
```

This will print the password:
 ```
secureAdminPassword4VotingMachineManagement
```


Getting the Flag
----------------
Once you have the admin password, you can log into the `management` page and view (fake) auth logs from the system. The flag is shown at the end of this file as an RSA finterprint

```
voterreg sshd[338]: Accepted publickey for git from 129.21.1.40 port 33740 ssh2: RSA F1:A6:FA:11:C0:DE:CO:11:DE:5L:0C:AL:E5
voterreg sshd[338]: pam_unix(sshd:session): session opened for user git by (uid=0)
```

The flag is `FA11C0DECO11DE5L0CALE5` (Fail code collides locales)
