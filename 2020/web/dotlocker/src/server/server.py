import os
from functools import wraps

from flask import Flask, request, abort, send_from_directory, render_template, session, redirect, url_for

import db
import admin

"""
Keeping this here for safe keeping:

flag{0ff_by_sl4sh_n0w_1_hav3_y0ur_sourc3}

"""

app = Flask(__name__)
with open('secret','rb') as f:
    app.config['SECRET_KEY'] = f.read()[:32]

def csrf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'GET':
            return f(*args, **kwargs)

        token = request.form.get('_csrf_token',None)
        _id = request.form.get('_id',None)
        if (not token or not _id) and request.is_json:
            token = request.json.get('_csrf_token',None)
            _id = request.json.get('_id',None)

        if token and _id and db.valid_csrf(token, _id):
            if not _id == session['_id']:
                abort(401)

            return f(*args, **kwargs)

        abort(403)

    return decorated

@app.route('/', methods=['GET','POST'])
def index():
    return redirect(url_for('get_all_files'))

@app.route('/new')
def new():
    return render_template('edit.html',data='', name='New Dotfile')

@app.route('/new/etc/<path:path>')
def new_path(path):
    if '..' in path or path[0] == '/':
        abort(403)
    path_n = os.path.join('/etc',path)
    path_n = os.path.realpath(path_n)
    if not path_n.startswith('/etc/') or '..' in path_n:
        abort(403)

    data = ''
    if os.path.exists(path_n) and os.path.isfile(path_n):
        try:
            with open(path_n,'r') as f:
                data = f.read()
        except:
            abort(500)
            pass

    return render_template('edit.html',data=data,name=os.path.basename(path) if data else 'New Dotfile')

@app.route('/get/<path:path>')
def get(path):
    return send_from_directory('/etc', path)

@app.route('/search', methods=['POST'])
def search():
    u = db.get_user_by_name(request.form['name'])
    if not u:
        return render_template('error.html',msg='Sorry, we could not find a user named ',white=request.form['name'])
    return redirect(url_for('public',id=u['_id']))


@app.route('/public/<string:id>')
def public(id):
    u = db.get_user(id)
    if not u:
        return render_template('error.html',msg='Sorry, we could not find this user')
    return render_template('files.html', user=u, public=True,
            count=len([x for x in u['dotfiles'].values() if x.get('public',False)]))

@app.route('/public/<string:id>/<string:name>')
def get_public(id, name):
    u = db.get_user(id)
    if not u:
        return render_template('error.html',msg='Sorry, we could not find this user')
    safe = db.safe_name(name)
    if not safe in u['dotfiles']:
        return render_template('error.html',msg='Sorry, we could not find a file named ',white=name)

    file = u['dotfiles'][safe]
    if not file.get('public', False):
        return render_template('error.html',msg='Sorry, we could not find a file named ',white=name)

    return render_template('edit.html', data=file['data'], name=file['name'])

@app.route('/save', methods=['POST'])
@csrf
def save():
    if not 'name' in request.form or not 'text' in request.form:
        abort(400)
    name = request.form['name'][:255]
    text = request.form['text'][:0x1000*0x1000]

    if len(name) == 0:
        abort(400)

    u = db.get_user(session['_id'])
    db.add_dotfile(u, name, {'data':text})

    return redirect(url_for('get_file', name=db.safe_name(name)))


@app.route('/files')
def get_all_files():
    u = db.get_user(session['_id'])
    return render_template('files.html', user=u, public=False)


@app.route('/files/<string:name>')
def get_file(name):
    u = db.get_user(session['_id'])
    name = db.safe_name(name)

    if not name in u['dotfiles']:
        return redirect(url_for('new'))

    file = u['dotfiles'][name]

    return render_template('edit.html', data=file['data'], name=file['name'])

@app.before_request
def before_request():
    if not '_id' in session:
        u = db.get_or_add_user()
        session['_id'] = str(u['_id'])

def get_csrf_token():
    if not '_id' in session:
        abort(500)
    u = db.get_user(session['_id'])
    if not u:
        abort(500)
    return u['csrf']

app.jinja_env.globals['get_csrf_token'] = get_csrf_token

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', msg='Sorry, we could not find this page...')

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', msg='Our bad... ', white='There was a server error')

"""
admin username: admin

ADMIN ROUTES
/admin/friends_only/share_link
"""
app.register_blueprint(admin.admin_routes, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

