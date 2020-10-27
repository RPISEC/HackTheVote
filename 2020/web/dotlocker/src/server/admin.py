import base64
import threading
import subprocess
from urlparse import urlparse

from flask import request, abort, Blueprint, session, redirect, render_template

import db

# XXX Change this to be the correct url to access this challenge
URL = 'http://dotlocker.hackthe.vote'

admin_routes = Blueprint('admin', __name__)
with open('./secret', 'rb') as f:
    CHROME_SECRET = f.read()[32:].strip()

def start_chrome(data):
    u = URL + '/admin/{secret}/{data}'.format(
            secret=CHROME_SECRET, data=base64.b64encode(data))
    print u
    subprocess.Popen(['node','/chrome.js',u]).wait()

@admin_routes.route('/<key>/<data>')
def admin(key, data):
    if key != CHROME_SECRET:
        abort(404)

    session['_id'] = str(db.get_user_by_name('admin')['_id'])
    session['admin'] = True
    return redirect(base64.b64decode(data))

@admin_routes.route('/friends_only/share_link', methods=['GET','POST'])
def share():
    if request.method == 'GET':
        return render_template('share_link.html')

    if session.get('admin',False):
        return 'bad'

    url = request.form['url']
    try:
        url_data = urlparse(url)
        if not url_data.scheme in ['http','https']:
            return render_template('share_link.html', bad=True)
    except:
        return render_template('share_link.html', bad=True)

    t = threading.Thread(target=start_chrome, args = (url,))
    t.daemon = True
    t.start()
    
    return render_template('share_link.html', good=True)

    return ''







