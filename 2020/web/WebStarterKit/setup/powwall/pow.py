import os
import time
import binascii
from werkzeug.exceptions import HTTPException
from hashlib import sha256

from flask import render_template, session, request, jsonify

class PowException(Exception):
    def __init__(self, response):
        Exception.__init__(self)
        self.response = response

class POW():
    # *diff* specifies how hard the POW should be. If its too hard (>4) the
    #   browser might hang with no progress (default is 4)
    # *count* is the number of pows that need to be solved. Increase this to make
    #   the overall pow harder (default is 6)
    # *pow_path* is the path to get the latest pow goal (default is '/pow/refresh')
    #   this is used for the flask route. If you want to specify a url use *pow_url*
    # *to* is how long the pow is valid for. Only set if using client side sessions
    def __init__(self, app, pow_path='/pow/refresh',pow_url=None, diff=4, count=6, to=0):
        self.app = app
        self.diff = diff
        self.count = count
        self.to = to
        self.pow_path = pow_path
        if pow_url is None:
            self.pow_url = self.pow_path
        else:
            self.pow_url = pow_url

        @app.route(pow_path)
        def get_pow():
            self.refresh_pow()
            return jsonify(pow=session['pow'])

        @app.errorhandler(PowException)
        def handle_PowException(exp):
            return exp.response


    def refresh_pow(self):
        session['pow'] = binascii.hexlify(os.urandom(self.diff)).decode('latin-1').lower()[:self.diff]
        session['pow_time'] = int(time.time())

    # Call pow to require validation
    # *template* what template file to render (default is "pow.html")
    #       NOTE make sure to edit templates/pow.html if not specified
    # Any other args are passed to the template
    def validate_pow(self, template='pow.html', **args):
        # If getting this endpoint, serve the pow page
        if request.method == 'GET' or not 'pow' in session or not 'pow_time' in session:
            self.refresh_pow()
            raise PowException(
                render_template(
                    template,
                    pow_url=self.pow_url,
                    pow_count=self.count,
                    **args))

        sol = request.form['pow'].split(';')

        if self.to > 0 and int(time.time()) > session['pow_time'] + self.to:
            pow_good = False
        elif len(sol) != self.count:
            pow_good = False
        else:
            # Verify the pow solutions
            used = []
            pow_good = True
            for s in sol:
                if s in used:
                    pow_good = False
                    break

                ver = sha256(s.encode('latin-1')).hexdigest()
                if ver[:self.diff] != session['pow']:
                    pow_good = False
                    break

        self.refresh_pow()

        if not pow_good: 
            raise PowException(
                render_template(
                    template,
                    pow_url=self.pow_url,
                    pow_count=self.count,
                    error='Invalid POW...',
                    **args))

        return True
