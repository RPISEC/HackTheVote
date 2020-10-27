Boxes of Ballots
---

####Leaking information
Interestingly enough, we don't get any source code for the
application. But we do get the partial input
```
ebug": true, "data": "BBBBBBBBBBBBBBBB", "op": "enc"}
```
Taking a guess that the partial parameter is `debug` we get
```
{"debug": true, "data": "BBBBBBBBBBBBBBBB", "op": "enc"}
[+] Remote Debugging Enabled
Traceback (most recent call last):
  File "./blocks.py", line 115, in dataReceived
    self.key = encData['key']
KeyError: 'key'
```
Setting the `key` to something allows us to encrypt data.
```
{"debug": true, "data": "BBBBBBBBBBBBBBBB", "op": "enc", "key": "AAAAAAAAAAAAAAAA"}
[+] Remote Debugging Enabled
{"Status": "ok", "data": "0134c8a2c19a4c9af41d8dd5f34916e0"}
```
If we set `debug` to `false`
```
{"debug": false, "data": "BBBBBBBBBBBBBBBB", "op": "enc", "key": "AAAAAAAAAAAAAAAA"}
[+] Remote Debugging Enabled
{"Status": "ok", "data": "adf983dcb5f1d388ba06074330c0b9194376b61c668693277c00a5f3649fdea4b7f7e2e12ce6610fd54de6768483bcb5"}
```
Of course that would be too easy, and the key argument is ignored, and the real key is used. But our
ciphertext is considerable longer than it should be. Could they be appending data to our ciphertext?

If we make the key the incorrent length
```
{"debug": true, "data": "BBBBBBBBBBBBBBBB", "op": "enc", "key": "AAAAAAAAAAAAAAA"}
[+] Remote Debugging Enabled
Traceback (most recent call last):
  File "./blocks.py", line 97, in encrypt_data
    enc = encrypt_cbc(self.key, self.iv, encData['data'])
  File "./blocks.py", line 62, in encrypt_cbc
    ctxt = encrypt_block(key,ctxt)
  File "./blocks.py", line 28, in encrypt_block
    encobj = AES.new(key, AES.MODE_ECB)
  File "/usr/lib/python2.7/dist-packages/Crypto/Cipher/AES.py", line 94, in new
    return AESCipher(key, *args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/Crypto/Cipher/AES.py", line 59, in __init__
    blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/Crypto/Cipher/blockalgo.py", line 141, in __init__
    self._cipher = factory.new(key, *args, **kwargs)
ValueError: AES key must be either 16, 24, or 32 bytes long
```
We can confirm again that they don't mutate our input in debug mode.

####Recovering secret
The server appends data to user input, and then encrypts it.

In a block cipher, this can end up like
```
UUUUUUUUUUUUUUUS
```
where U is user data and S is secret.

An attacker simply makes a map of all 256 possible ciphertexts, and then does a lookup.
This can be performed again and again to fully recover the appended secret.
