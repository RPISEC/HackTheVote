# SocialIsolation Second Flag

This flag involved exploiting a weakness in chrome's site-isolation feature: subdomains are not isolated.

We just need to get arbitrary read/write on a subdomain (or main domain) of the site with the flag. Once we do that we can use `m_universal_access` to give us read to an iframe of any other subdomain. (ie `stuff.google.com` can iframe and read content from `google.com`)

We can use [pwn.c](./pwn.c) to do the pointer derefs we need to find `m_universal_access`

Once we do that we use [sol2.js](./sol2.js) to attach the iframe and then access its content directly! Normally this is never allowed but with the magic of `m_universal_access` it works!
