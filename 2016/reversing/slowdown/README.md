Reversing 300

Slowdown

Flag: flag{pl3nty_0f_pr!mes_t0_g0_@round}

State: OK
Influence: -3
Reaction: -6



Just saw this on CTFNN, looks like the DNC hired some top notch consulants to fix their cyber problems.

> CTF News Network: So, how can you be sure these servers are secure this time around?
> Consultant:  It took a /long time/ to generate the keys that let you log into them. 
> CTF News Network: Wow, thats great. When will they be ready?
> Consultant: Everything's live already! I did all the work in the past few days! 
> CTF News Network: A true national cyber hero! We'll have more on this story at 13:37.

Thats as sketch as it gets. Our inside man managed to exfil an ip address of one of the servers, a pubkey, and the libcrypto that was on the box. I bet there's some good stuff on it.

`ssh slowdown@slowdown.pwn.democrat`

[id_rsa](https://s3.amazonaws.com/hackthevote/id_rsa.8f413ca1bdcd5bbfc3455195ddddaaf5efbbf66261a3dd440b5702636674e2bb.pub)
[libcrypto](https://s3.amazonaws.com/hackthevote/libcrypto.so.1.0.0.12e54c010aef4ee5464b25863e68f4c9e6f47c0adecfd11a96c0aae3f9c68626)
