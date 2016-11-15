This challenge was an openIpCamera filesystem image, which was backdoored.

You had to find the backdoor and use it on the live one.

- Extract the filesystem image, find the camera binary in /bin
- Extract the camera binary using gunzip_bflt.pl. (find it by googleing the output of file)
- Locate the cgi code in the camera binary
- Looking at the cgi switch case, they all start with the same auth function, but snapshot.cgi has extra code
    o This function calls to a code cave
    o It is checking for some xor'ed parameters
    o Un-xor the parameters to get B4cKD00rdCam and H4ck3rA774ck
- Now figure out where the comparisons come from
- There is a sort of hashtable that they are being loaded from, xref that to see the store
- It is stored in the http parsing code, after parsing ? and splitting at = so clearly url parameters
- Go to /snapshot.cgi?B4cKD00rdCam=H4ck3rA774ck
- Refresh until flag is visible, and also grab the admin password for the next level
