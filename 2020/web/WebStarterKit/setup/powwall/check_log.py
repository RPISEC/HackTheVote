import os
import time
import json
import subprocess

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

THRESHOLD = 50
TIMEOUT = 10*60

seen = {}

logs = subprocess.check_output('dmesg').decode('latin-1')
for l in logs.split('\n'):
    c = l.split(']',1)[-1].strip()
    if not c.startswith('INPUT:ACCEPT'):
        continue
    v = {p[0]:p[-1] for p in (e.split('=',1) for e in c.split())}

    ip = v['SRC']

    if not ip in seen:
        seen[ip] = 1
    else:
        seen[ip] += 1


bad = []
for ip,t in seen.items():
    if t < THRESHOLD:
        continue

    try:
        # Remove access if not expired yet
        res = subprocess.check_output(
            f'sudo iptables -L FORWARD -n --line-numbers | grep {ip}', shell=True).decode('latin-1')
        id = res.split()[0]
        subprocess.call(f'sudo iptables -D FORWARD {id}', shell=True)
    except subprocess.CalledProcessError:
        pass
    bad.append(ip)

cb = {}
if os.path.exists('bad.json'):
    with open('bad.json','r') as f:
        cb = json.load(f)
for ip in bad:
    cb[ip] = int(time.time() + TIMEOUT)

with open('bad.json','w') as f:
    f.write(json.dumps(cb))

subprocess.call('sudo dmesg -C', shell=True)
