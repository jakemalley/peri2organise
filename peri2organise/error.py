# error.py
# Jake Malley
# Error handling for the application.

# Flask Imports
from flask import render_template
# Application Imports
from peri2organise import app

# Create a error handler for HTTP errors.
def http_error_handler(error):
    return render_template("error/error.html", error=error)

# Apply this handler for specific HTTP error codes
for error in (400, 401, 403, 404, 405, 500, 502):
    app.error_handler_spec[None][error] = http_error_handler
