This challenge involves leaking server source using a nginx misconfiguartion, and then abusing a mongdb injection to leak a CSRF token and XSS the admin

## Info

Name: DotLocker

Description:
```
Dotfiles are the most important part of a hacker's life. Now you can keep them safe and share them with friends!
```

Flag 1: `RAWR{0ff_by_sl4sh_n0w_1_hav3_y0ur_sourc3}`

Points: 200? (how hard would the nginx thing be to figure out?)

Solution Description: Read the nginx config files and use off-by-slash to leak the server source

Hint: Look for problems with the nginx config

---

Name: DotLocker 2

Description:
```
Why should I worry, these dotfiles are so safe I even store my flag files in here!
```

Flag 2: `RAWR{JSON_c4n_b3_d4ng3rous_ar0und_n0sq1__m0ngo_pl5}'`

Points: 300-400?

Solution Description: Use Mongodb injection in the CSRF check (when using JSON) to side-channel leak the admin's CSRF token. Use this to upload an XSS payload to her account and steal her secret dotfiles

## Setup:

1. Change the URL in `./server/admin.py` to point to the correct one for this challenge when live
2. Deploy docker image

## Solution:

Flag 1:
1. We see that the new dotfile templates are being loaded from /etc/skel/, but we can actually access anything in /etc, so we can leak the nginx config with /new/nginx/sites-enabled/default
2. In this config we see that there is a slash missing from the static path, which allows us to directory traverse up a level and read source with /static../server.py
3. The first flag is in the source code

Flag 2:
1. With the source code we can see that the admin will visit a link you give her. However we cannot directly use this for CSRF because there is a CSRF token...
2. We can see the CSRF tokens are stored in mongodb with the user data. We can find a mongodb injection point when the CSRF token is checked for JSON data.
3. We can get the admin's mongodb ObjectId by searching for her on the site
4. We can send crafted `_csrf_tokens` like this `{"_csrf_token":"$regex":"^a.*$"}` to leak the csrf token via side-channel
5. With the admin's CSRF token we could now upload a dotfile to her account
6. Looking at the dotfile syntax highlighter we see it uses a javascript template string to escape html. However for one case it does `e(...)` instead of `e...` which will not escape correctly.
7. So we can inject scripts like this: `if [ <img src=x onerror="alert(1)"> ]; then`
8. We upload a XSS payload to the admin's account and look at her files. We find flag.txt, loading that we get the flag
