import re
import secrets
import json
import uuid
import hashlib
import signal

import requests
from flask import Flask, render_template, abort, request, session, make_response
from flask_sse import sse

from huey import RedisHuey

from selenium_bot import visit_webpage

app = Flask(__name__)

with open('config.json', 'rb') as f:
    config = json.load(f)
app.secret_key = config['secret_key']

BOT_RESP_SECRET = config['bot_secret']
HASH_SUFFIX_BYTES = config['hash_suffix_bytes']
LOCAL_SERVER_URL = config['local_server_url']

huey = RedisHuey('webchal', host=config['redis_host'], port=config['redis_port'])
app.config["REDIS_URL"] = f"redis://{config['redis_host']}:{config['redis_port']}"
app.register_blueprint(sse, url_prefix='/stream')


@huey.pre_execute()
def timeout_start(task):
    signal.alarm(20)


@huey.post_execute()
def timeout_stop(task, value, exc):
    signal.alarm(0)


@huey.task()
def visit_url(req_id, url):
    output = visit_webpage(url)
    requests.post(f'{LOCAL_SERVER_URL}/bot_resp/{str(req_id)}', data={'message': output, 'token': BOT_RESP_SECRET})


@app.route('/bot_resp/<uuid:req_id>', methods=['POST'])
def resp(req_id):
    if request.form.get('token') != BOT_RESP_SECRET:
        abort(404)
    msg = request.form.get('message')
    sse.publish({"message": msg}, channel=str(req_id))
    return ""


@app.route('/', methods=['GET'])
def index():
    session['hash_suffix'] = secrets.token_hex(HASH_SUFFIX_BYTES)
    return render_template('index.html', req_id=str(uuid.uuid4()), hash_suffix=session['hash_suffix'])


@app.route('/submit/<uuid:req_id>', methods=['POST'])
def submit_request(req_id):
    hash_input = request.form.get('hash_input')

    if hash_input is None:
        return "No hash input given"

    computed = hashlib.sha256(hash_input.encode()).hexdigest()
    if not computed.endswith(session["hash_suffix"]):
        return "Bad proof of work"

    session['hash_suffix'] = secrets.token_hex(HASH_SUFFIX_BYTES)

    url = request.form.get('url')

    if url is None:
        return "Forgetting something?"

    url = str(url)

    if len(url) > 500:
        return "That's a really long URL..."

    if not url.startswith('http'):
        return "Yeah we don't speak that protocol here"

    if '@' in url:
        return '\U0001F6AB\U0001F34A'

    visit_url(str(req_id), url)

    return "Submitted, waiting for bot..."


@app.route('/playground')
def playground():
    payload = request.args.get('payload')
    resp = make_response(render_template('playground.html', payload=payload))
    resp.headers['Content-Security-Policy']='sandbox allow-scripts;'
    return resp


@app.route('/challenge')
def challenge():
    payload = request.args.get('payload', '')
    if len(payload) > 100:
        return "No"

    payload = re.sub(r'[^a-zA-Z0-9()\[\]_;"`]', '', payload)
    resp = make_response(render_template('challenge.html', payload=payload))
    if request.cookies.get('flag') is None:
        resp.set_cookie('flag', 'the bot has the real flag', path='/challenge')
    return resp


@app.route('/robots.txt')
def robots():
    return open('bg.png', 'rb').read(), 200, {'Content-Type': 'image/png'}
