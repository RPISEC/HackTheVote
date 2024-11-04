#!/usr/bin/env python3
import string
from hashlib import sha512
from os import chdir, environ
from pathlib import Path
from secrets import token_hex
from subprocess import PIPE, Popen, run

from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)


app = Flask(__name__)
app.secret_key = environ['SECRET_KEY']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['DATA_DIR'] = '/tmp/graph/'


def userdir():
    if "user" not in session:
        return Path('/bad/')
    return Path(app.config['DATA_DIR'], session["user"])


def isfilename(s):
    return s and all(
        c in string.ascii_uppercase + string.ascii_lowercase + string.digits + '_-'
        for c in ''.join(s.split('.', 1))
    )


@app.route("/")
def index():
    return render_template("index.jinja", authed="user" in session)


@app.route("/source")
def source():
    return send_file(__file__, as_attachment=True)


@app.route("/data", methods=["GET"])
def data():
    return render_template(
        "data.jinja",
        authed="user" in session,
        filenames=[p.name for p in userdir().glob('*.csv')],
    )


def convert(filename, contents):
    for line in contents.rstrip('\n').split('\n'):
        if ',' not in line or ' ' in line:
            return False
    with open(filename, 'w') as f:
        f.write(contents)
    out = run(
        ['sandbox.sh', 'mlr', '--icsvlite', '--opprint', '-N', 'cat', filename],
        capture_output=True,
    ).stdout
    with open(filename, 'wb') as f:
        f.write(out)
    return True


@app.route("/getfile/<filename>")
def getfile(filename):
    if "user" not in session:
        return make_response("unauthorized", 401)
    return send_from_directory(userdir(), filename, as_attachment=True)


@app.route("/data", methods=["POST"])
def upload_csv():
    if "user" not in session:
        return make_response("unauthorized", 401)
    if 'csv' not in request.files:
        flash('no file part')
        return redirect(url_for('data'))
    file_ = request.files['csv']
    if file_.filename == '':
        flash('no selected file')
        return redirect(url_for('data'))
    if file_.mimetype != 'text/csv':
        flash('please upload a csv')
        return redirect(url_for('data'))
    if not isfilename(file_.filename):
        flash('bad filename')
        return redirect(url_for('data'))
    try:
        chdir(userdir())
    except OSError:
        flash('invalid session')
        return signout()
    contents = file_.read().decode()
    if not convert(file_.filename, contents):  # Write file
        flash('failed to convert file')
        return redirect(url_for('data'))
    return redirect(url_for('data', filename=file_.filename))


@app.route("/graph", methods=["GET"])
def graph():
    return render_template(
        "graph.jinja",
        authed="user" in session,
        filenames=[p.name for p in userdir().glob('*.csv')],
        result=request.args.get('result'),
    )


def gnuplot(in_filename, out_filename, points):
    plot = f"""
set terminal png size 2048,512
set output '{out_filename}'
set nokey
plot '{in_filename}' with {points}
"""
    p = Popen(['sandbox.sh', 'gnuplot'], text=True, stdin=PIPE, stderr=PIPE)
    output = p.communicate(input=plot)[1:]
    return p.returncode, output


@app.route("/graph", methods=["POST"])
def render_graph():
    # TODO consider adding POW here to reduce server resource usage
    if "user" not in session:
        return make_response("unauthorized", 401)
    in_filename = request.form.get('in')
    if not isfilename(in_filename):
        flash('invalid input filename')
        return redirect(url_for('graph'))
    out_filename = request.form.get('out', ' ') + '.png'
    if not isfilename(out_filename) or out_filename == '.png':
        flash('invalid output filename')
        return redirect(url_for('graph'))
    points = request.form.get('points')
    if points not in ('points', 'lines', 'linespoints'):
        flash('invalid points setting')
        return redirect(url_for('graph'))

    try:
        chdir(userdir())
    except OSError:
        flash('invalid session')
        return signout()
    ret, output = gnuplot(in_filename, out_filename, points)
    if ret == 0:
        return redirect(url_for('graph', result=out_filename))
    else:
        flash('<pre>' + '\n'.join(output) + '</pre>')
        return redirect(url_for('graph'))


@app.route('/signin')
def signin():
    # TODO pow/captcha here
    if "user" not in session:
        if sha512(request.args.get('admin', '').encode()) == environ['ADMINHASH']:
            session[
                "user"
            ] = '872bfdd01752ea2641a3e211db6127a7af1d9b44f1602780bbae465ccf4ac25e'
        else:
            session["user"] = token_hex()
        Path(app.config['DATA_DIR'], session["user"]).mkdir(parents=True, exist_ok=True)
    return redirect(url_for("index"))


@app.route("/signout")
def signout():
    if "user" in session:
        del session["user"]
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
else:
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
