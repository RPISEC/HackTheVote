## Notes

* `tc.mp4` is a "hybrid" mp4 with a truecrypt volume embedded in a fake data section (truecrypt can read this)
    * The truecrypt volume only has `keys.png` as a keyfile, no password
    * Right now it only contains `flag.txt`. If the flag is ever changed, it needs to be updated inside the tc volume
* `make_7z.sh` will make the final 7z for the challenge using `pass.txt` as the password
