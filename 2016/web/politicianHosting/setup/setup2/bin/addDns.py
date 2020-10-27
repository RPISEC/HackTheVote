import sys
import os
import subprocess
import re

# [name] [ip]
# 1 = arg wrong
# 2 = name wrong
# 3 = ip wrong

HOSTS = '/var/www/chals/voteforme/hosts'
HOSTS = '/etc/hosts'

os.environ['HOSTALIASES']= HOSTS

if len(sys.argv)<3:
    exit(-1)

name = sys.argv[1]
ip = sys.argv[2]

if re.match('^[a-zA-Z0-9]{1,32}\.DOMAIN$',name)==None:
    print name,"failed re"
    exit(-2)
if re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip)==None:
    print ip,"failed re"
    exit(-3)

f = open(HOSTS,'r')
d = f.read()
f.close()
data = d.split('\n')[:-1]
found = False
for i,l in enumerate(d.split('\n')):
    ls = l.split(' ')
    if len(ls)>1:
        if ls[1]==name:
            data[i] = "%s %s"%(ip,name)
            found = True
            break
if not found:
    data.append("%s %s"%(ip,name))

f = open(HOSTS,'w')
f.write('\n'.join(data)+'\n')
f.close()
        
   
