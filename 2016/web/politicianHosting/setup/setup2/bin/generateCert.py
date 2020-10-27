import subprocess
import os
import socket
import urllib2
import sys
import re
import json
import ssl

if len(sys.argv)<6:
    print "not enough args",sys.argv
    exit(1)
# [ip] [port] [token] [name] [csr]
# 1 = args wrong
# 2 = Failed request
# 3 = Failed token
# 4 = CSR inavlid
# 5 = CN does not match
# 6 = CN is invalid

if len(sys.argv[4])>40:
    exit(6)
if re.match('^[a-zA-Z0-9]+\.DOMAIN$',sys.argv[4])==None:
    print sys.argv[4],"re failed"
    exit(6)


if re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',sys.argv[1])==None:
    print "IP RE failed"
    exit(2)

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen('https://%s:%s/dns_token'%(sys.argv[1],sys.argv[2]),context=ctx) 
except Exception as e:
    print e
    exit(2)
html = response.read()
if html[:32]!=sys.argv[3][:32]:
    exit(3)


p=subprocess.Popen(['openssl','req','-subject','-noout'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
#f = open(sys.argv[1],'r')
#d = f.read()
#f.close()
subject = {}
d = sys.argv[5]
d2,good = p.communicate(d)
d2 = d2[:-1].split('/')
cn = None
for s in d2:
    nad=s.split('=',1)
    if len(nad)>1:
        subject[nad[0]]=nad[1]
    if s[:3]=='CN=':
        if cn!=None:
            print "Too many CN!!!"
            exit(4)
        else:
            cn = s[3:]
if cn==None:
    print "No CN!"
    exit(4)
if cn!=sys.argv[4]:
    print "Not the same name"
    exit(5)


if re.match('^[a-zA-Z0-9]+\.DOMAIN$',cn)==None:
    print "doesn't match"
    exit(6)
    
#TODO check if site is valid
os.write(2,"Singing cert now "+repr(d)+"\n")

p = subprocess.Popen(['openssl','x509','-req','-CA','WEB_DIR/keys/CA.cert.pem','-CAkey','/var/www/tld/keys/CA.key.pem','-CAcreateserial',
    '-days','500'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

d2,e = p.communicate(d)
if e[:12]!="Signature ok":
    exit(4)
if d2=="":
    print e
    exit(4)
print json.dumps(subject)
print d2

exit(0)
