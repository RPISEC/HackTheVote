#!/usr/bin/env python3

import re
import os
import time
import json

import subprocess

from flask import Flask, request, jsonify, redirect, url_for, make_response
from flask_session import Session
import requests

from pow import POW

TARGET_IP = '192.111.137.73'
TARGET_PORT = 28080
LOCAL_PORT = 28080
POW_SERVER_PORT = 28081

TIME = 60*15

MY_IP = "webstarterkit.hackthe.vote"
print(f"{MY_IP}:{POW_SERVER_PORT}")

def getRemoteIp():
    trusted_proxies = {'127.0.0.1'}
    route = request.access_route + [request.remote_addr]

    remote_addr = next((addr for addr in reversed(route)
                    if addr not in trusted_proxies), request.remote_addr)
    return remote_addr

app = Flask(__name__)

# NOTE Required so that the pow session can't be reused
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Make sure ip forwarding is on
subprocess.call('sudo sysctl net.ipv4.ip_forward=1', shell=True)

r = subprocess.check_output('sudo iptables -L PREROUTING -n -t nat',shell=True).decode('latin-1')
if len(r.strip().split('\n')) < 3:
    print('No PREROUTING rule found, installing one')
    subprocess.call(f'sudo iptables -P FORWARD DROP', shell=True)
    subprocess.call(f'sudo iptables -t nat -A PREROUTING -p tcp --dport {LOCAL_PORT} -j DNAT --to-destination {TARGET_IP}:{TARGET_PORT}', shell=True)
    subprocess.call(f'sudo iptables -t nat -A POSTROUTING -j MASQUERADE', shell=True)

# Setup Accept Logging
subprocess.call('sudo iptables -N LOG_ACCEPT', shell=True)
subprocess.call('sudo iptables -F LOG_ACCEPT', shell=True)
subprocess.call('sudo iptables -A LOG_ACCEPT -j LOG -p tcp --syn --log-prefix "INPUT:ACCEPT:" --log-level 6', shell=True)
subprocess.call('sudo iptables -A LOG_ACCEPT -j ACCEPT', shell=True)


# reset FORWARD chain
subprocess.call(f'sudo iptables -F FORWARD', shell=True)
# make sure the default policy is DROP
subprocess.call(f'sudo iptables -P FORWARD DROP', shell=True)
# allow target to respond
subprocess.call(f'sudo iptables -A FORWARD -p tcp -s {TARGET_IP} -j ACCEPT', shell=True)

# Declare pow for the current app
# *diff* specifies how hard the POW should be. If its too hard (>4) the
#   browser might hang with no visible progress (default is 4)
# *count* is the number of pows that need to be solved. Increase this to make
#   the overall pow harder (default is 6)
# *pow_path* is the path to get the latest pow goal (default is '/pow/refresh')
#   this is used for the flask route. If you want to specify a url use *pow_url*
# *to* is how long the pow is valid for. Only set if using client side sessions
pow = POW(app, diff=4, count=6)

# NOTE Make sure to catch both GET and POST to serve the pow page
@app.route('/',methods=['GET','POST'])
def test():
    global LOCAL_PORT
    pow.validate_pow(local_port=LOCAL_PORT)

    ip = getRemoteIp()

    if os.path.exists('bad.json'):
        with open('bad.json') as f:
            bad = json.load(f)
        if ip in bad and time.time() < bad[ip]:
            left = int(bad[ip] - time.time())
            return f'You are making requests too fast! Please try again in {left} seconds'
    try:
        res = subprocess.check_output(
            f'sudo iptables -L FORWARD -n --line-numbers | grep {ip}', shell=True).decode('latin-1')
        exp = int(res.split('expire=')[1].split()[0])

        if exp > time.time():
            res = make_response(redirect(url_for('test')))
            res.set_cookie('exp',str(exp))
            return res

    except subprocess.CalledProcessError:
        pass

    exp = int(time.time() + TIME)

    # Add new rule allowing them to access until the exp (NOTE NEED CRON JOB TO EXP)
    subprocess.call(['sudo','iptables','-A','FORWARD','-s',ip,'-m','comment', '--comment',f'expire={exp}','-j','LOG_ACCEPT'])

    res = make_response(redirect(url_for('test')))
    res.set_cookie('exp',str(exp))
    return res

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=28081)

