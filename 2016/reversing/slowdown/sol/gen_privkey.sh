#!/bin/bash
# https://stackoverflow.com/questions/19850283/how-to-generate-rsa-keys-using-specific-input-numbers-in-openssl
openssl asn1parse -genconf privkey.asn1 -out privkey.der
openssl rsa -in privkey.der -inform der -text -check | tail -n51 > id_rsa

