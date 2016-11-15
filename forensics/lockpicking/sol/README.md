# Lockpicking

### Separating files
There are a total of 3 files you need from `lockpick.png` like this:

```
[lockpick png (visible)][7z archive][keys png]
```

Only the 2 pngs can be found with a file carver (e.g. `foremost`), the 7z has to be found manually because the first byte was changed (`'7' -> '8'`). This isn't too difficult to find, you might notice that the two pngs extracted by a carver are way off the total file size.

### 7z password
Once you have the 7z, you'll find that it's password protected. The password is stored in lsb in `lockpick.png` (blue plane 0). You could use something like like StegSolve or just code something yourself, either way -> 'SuperS3cur3P4ssw0rdTh4tY0uW1llN3v3rEv3rGu3s5OrBr00tf0rceMuahahahaha'


### S3CR3T
You extract it out, and you get `S3CR3T`, which turns out to be an `mp4`. You can watch it, I tried to make it entertaining, but it's not necessary. This is the fun part, this `mp4` is actually a [hybrid mp4 / truecrypt volume](http://bfy.tw/8bWV). Truecrypt is able to recognize this like any other volume, but you have to use the picture of **keys** as the keyfile, there is no password. Inside the volume is `flag.txt`, and you get the flag:

```
flag{p4dl0ck5_us3_A3S_n0w4d4ys_wh0_kn3w}
```
