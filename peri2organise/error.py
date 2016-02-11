# error.py
# Jake Malley
# Error handling for the application.

# Flask Imports
from flask import render_template
from flask import request
from flask import url_for
# Application Imports
from peri2organise import app
# Imports
from urlparse import urlparse
from urlparse import urljoin

# Securely redirecting back - based on http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.referrer, url_for('home.index'):
        if not target:
            continue
        if is_safe_url(target):
            return target

# Create a error handler for HTTP errors.
def http_error_handler(error):
    return render_template("error/error.html", error=error, redirect_back=get_redirect_target())

# Apply this handler for specific HTTP error codes
for error in (400, 401, 403, 404, 405, 500, 502):
    app.error_handler_spec[None][error] = http_error_handler

