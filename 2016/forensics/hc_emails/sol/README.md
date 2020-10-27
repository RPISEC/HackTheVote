# Hillary's Emails - Forensics 500
>We suspect Hillary has been smuggling her emails over the border using some kind of underground passageway. Find out where she's hiding them and what secrets they contain

NOTE: alternate snapshot link [here](https://drive.google.com/open?id=0B8D2vqg5KC_odXdlRzVYaDV4VEk)

All you're given at the start of this challenge is a pcap
This challenge can be split up into 3ish parts

# Part 1 - DNS Tunnel
> "underground passageway" *cough* tunnel

The first part is dealing with the DNS traffic that makes up 99% of the pcap. Some quick googling should bring up a common tool used for DNS tunneling called `iodine`. Though not 100% necessary, one thing you can do here (thx cyberseed) is find out where the `iodined` server is running. You can see `hillary.clinton.io` everywhere in the pcap, so to find the server, do:

```bash
$ dig hillary.clinton.io +trace

; <<>> DiG 9.10.3-P4-Ubuntu <<>> hillary.clinton.io +trace
;; global options: +cmd
.                       12935   IN      NS      a.root-servers.net.
.                       12935   IN      NS      b.root-servers.net.
...
[REDACTED]
...

hillary.clinton.io.     3600    IN      NS      email.clinton.io. # <<<<<<<<< RIGHT HERE
;; Received 83 bytes from 69.197.18.162#53(ns3.afraid.org) in 81 ms

;; connection timed out; no servers could be reached
```

So now we know the server is running at `email.clinton.io`, and you can `nslookup` that to find its IP at `45.55.178.79`. Will come back to this later.

The goal right now is to decrypt the traffic so you can see what Hillary was doing. There's probably other ways to do that, but just googling it brings you to [this ctf writeup by StalkR](http://blog.stalkr.net/2010/10/hacklu-ctf-challenge-9-bottle-writeup.html), which gets you most of the way there.

Note though that the script from that blog post had two issues with it:

* If there were any packets it failed to decompress, it would just quit (like 20 packets in)
    * Easy workaround, when it fails, just discard whatever it tried to decompress and keep going
* There were a ton of `Popen`s for things that could be done in python, so I went ahead and made it so there were no `Popen`s. This is by no means necessary, but it really speeds things up

And of course you had to change the tld it looks for `.hillary.clinton.io.`, which is all over the pcap.

Final script in `sol/extract_dns.py`, output:

```bash
$ ./extract_dns.py
Successfully extracted 32502 packets into extracted.pcap
```

# Part 2 - Decrypted Traffic

Now that you've gotten a pcap out of that pcap, you can find out what hillary was doing! This new pcap contains a bunch of attempts at logging into Hillary's private server. Most of them are random failures, like:

```
login: clinton
password: +vwF~-HM]
ACCESS DENIED!
```

And there are a couple of successes in there too:

```
login: Jeb
password: !
Welcome, Jeb
```

Another thing you'll notice is the obviously suspicious IP/port that all of these are connecting to. And by suspicious I mean that's the IP we found before for `email.clinton.io`. So you can try connecting to it:

```bash
$ nc email.clinton.io 9999

+-----------------------------+
|       !!! WARNING !!!       |
| SYSTEM HAS BEEN LOCKED DOWN |
|     NON-ADMIN USERS ARE     |
|        NOW  DISABLED        |
+-----------------------------+

login: aaa
password: aaa
aaa is not an admin!

```

Ok, so now we know that we need to find an admin login/pass. Looking back at all the login attempts, there were only 4 different usernames that were attempted, you could try all those out with a random password:

```bash
$ nc email.clinton.io 9999
login: trump
password: aaa
trump is not an admin!

$ nc email.clinton.io 9999
login: Jeb
password: aaa
Jeb is not an admin!

$ nc email.clinton.io 9999
login: bernie
password: aaa
bernie is not an admin!

$ nc email.clinton.io 9999
login: clinton
password: aaa
ACCESS DENIED!
```

So `clinton` is the admin (are you surprised?), but now we need the password. This is pretty easy as soon as you notice any of the successful logins in the pcap, they all contain something like `Welcome, user`, so just search `Welcome, clinton` in wireshark, and you'll come across this stream:

```
login: clinton
password: IAmGoingToBeTheNextPresidentAndIWillDestroyTrump
Welcome, clinton
Now, to access your emails, enter the SUPER SECRET PASSWORD: uhhh....China?
+-------------------------+
|!!! INTRUDER DETECTED !!!|
|     THE EMAILS HAVE     |
|    BEEN  COMPROMISED    |
|  !!! WIPING DRIVES !!!  |
|  !!! WIPING DRIVES !!!  |
|  !!! WIPING DRIVES !!!  |
|!!! ENTERING LOCKDOWN !!!|
+-------------------------+
```

Great, so now login:

```bash
$ nc email.clinton.io 9999
+-----------------------------+
|       !!! WARNING !!!       |
| SYSTEM HAS BEEN LOCKED DOWN |
|     NON-ADMIN USERS ARE     |
|        NOW  DISABLED        |
+-----------------------------+

login: clinton
password: IAmGoingToBeTheNextPresidentAndIWillDestroyTrump
Welcome, clinton
+-----------------------------+
|       !!! WARNING !!!       |
|   EMAILS HAVE  BEEN WIPED   |
| A SYSTEM SNAPSHOT WAS TAKEN |
|     BEFORE THE INCIDENT     |
|                             |
| =========================== |
|       PRESS  ENTER TO       |
|        DUMP SNAPSHOT        |
+-----------------------------+
```

#### NOTE: due to connection issues with dumping the snapshot, this part was updated:
```bash
$ nc email.clinton.io 9999
+-----------------------------+
|       !!! WARNING !!!       |
| SYSTEM HAS BEEN LOCKED DOWN |
|     NON-ADMIN USERS ARE     |
|        NOW  DISABLED        |
+-----------------------------+

login: clinton
password: IAmGoingToBeTheNextPresidentAndIWillDestroyTrump
Welcome, clinton
+-----------------------------+
|       !!! WARNING !!!       |
|   EMAILS HAVE  BEEN WIPED   |
| A SYSTEM SNAPSHOT WAS TAKEN |
|     BEFORE THE INCIDENT     |
+-----------------------------+



Download the snapshot from http://email.clinton.io/[admin username]/[admin pass]/snapshot
$ wget http://email.clinton.io/clinton/IAmGoingToBeTheNextPresidentAndIWillDestroyTrump/snapshot
```

# Step 3 - The Emails

So now you'll have a file that `file` says is a `Microsoft Outlook email folder (>=2003)`. Look this up, and you'll find this is a type of MS Outlook archive (PST file). Now you **could** use one of those crap freeware pst viewers, but they're all a pain and can't even sort properly. A better approach would be either

1. Actually load it into outlook, probably the easiest way to sift through these. Oh did I mention there were a lot? Yeahhh there's like 24,000
2. There's an alternative library called [Redemption](http://www.dimastr.com/redemption/home.htm) that you can use to read the emails using any language that can use windows COM libraries (It does seem to be geared more toward visual studio languages though).

(I also hear `readpst` can be used here, buuuut ¯\\_(ツ)_/¯)
My solution uses the latter. Basically the steps to figuring this part out are:

* Sort and/or scroll through the emails a bit. There may be a lot of them, but with sorting it won't be long before you come across some suspicious emails from the address `cl1nt0nm4il3r@gmail.com`. There's your first filter, and now you're down to 33 emails.
* 33? Seems awfully flag lengthy doesn't it? At this point you might start looking through the metadata for these emails.
* One field will seem immediately out of place: the creation/sent on date. They all seem to be random dates in the future, but if you look at only the years:
    
    ```
    (in no particular order (yet...))
    2097, 2084, 2048, 2123, 2102, 2049, ...
    ```
    
    If you just ignore the 2's, you'll notice these are just ascii! :OOO

    ```
    97, 84, 48, 123, 102, 49, ...
    'a', 'T', '0', '{', 'f', '1', ...
    ```

* So what order do these need to be in? What else is in the email metadata that could be useful to sort by...the delivery date! They are all within a couple of days of each other, so the plan is to sort by those, and then hopefully get a flag out of the creation dates.

Here's my solution using `Redemption`:

```C#
using System;
using System.IO;
using System.Linq;
using Redemption;

namespace Solution {
    class Solve {
        static void Main(string[] args) {
            string path = Path.GetFullPath(@"..\..\..\snapshot.pst");

            // Load the PST
            RDOSession session = new RDOSession();
            session.LogonPstStore(path);

            // Grab everything in the inbox
            RDOItems inbox = session.GetFolderFromPath("PRIVATE INBOX").Items;

            // Filter out all emails from the flag mailer
            RDOItems spoofed = inbox.Restrict("[SenderEmailAddress]='cl1nt0nm4il3r@gmail.com'");

            // The flag is hidden in the send date (year),
            // sorted by the delivery date
            string flag = string.Concat(spoofed.OfType<RDOMail>()
                                               .OrderBy(m => m.ReceivedTime) // Sort by delivery date
                                               .Select(m => m.SentOn.Year - 2000) // Get the flag ordinal values
                                               .Select(c => (char) c)); // Convert to char
            Console.Out.WriteLine(flag);
        }
    }
}
```

And then this finally prints out the flag:

```
flag{w1k1L3ak5_g0T_n0tH1ng_0n_m3}
```
