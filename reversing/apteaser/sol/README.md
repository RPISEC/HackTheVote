APTeaser
---

You are given a PCAP that contains someone downloading a malicious application, which
then gets executed and begins to exfil data.

Extracting the malware from the PCAP and REing it reveals
that it takes a screenshot, encrypts it, and slowly exfils the data.

The malware encrypts and exfils the screenshot in chunks, using srand(time) and rand()
to generate an XOR keystream. This means each chunk has a different key stream.

Extract the time and ctxt from each of the exfil packets and decrypt the
ciphertext to get the screenshot. The flag can be seen in an email.
