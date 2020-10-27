Slowdown
---

*General*

The new lib generates RSA prime p in a rand() loop until it's "prime", causing the slowdown. It uses srand(time), so you can predict the rand seed.

Search seeds until you find the right p. You can check that it's the right p by verifying that it divides N evenly. Then just generate a private key to ssh into the server and get the flag.

Steps:
Get the seed and p,q
```
$ gcc find_seed.c -lssl -lcrypto -o find_seed
$ ./find_seed
```
Do some math and fill out privkey.asn1 with following information
```
asn1=SEQUENCE:rsa_key

[rsa_key]
version=INTEGER:0
modules=INTEGER:
pubExp=INTEGER:
privExp=INTEGER:
p=INTEGER:
q=INTEGER:
e1=INTEGER:$(d mod p-1)
e2=INTEGER:$(d mod q-1)
coeff=INTEGER:$(p^1 mod q)
```
Convert the asn1 to an ssh private key
```
$ ./gen_privkey.sh
```
Get the flag
```
$ ssh -i ./id_rsa slowdown@p.rpis.ec cat flag
```
