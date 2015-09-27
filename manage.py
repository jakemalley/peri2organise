# manage.py
# Jake Malley
# Uses flask-script to provide a management script.

# Flask Imports
from flask.ext.script import Manager
from flask.ext.script import Server
# Application Imports
from peri2organise import app

# Create a Manager object.
manager = Manager(app)

# Check to see if configuration has been set for development server.
try:
    DEVELOPMENT_SERVER_HOST = app.config['DEVELOPMENT_SERVER_HOST']
except KeyError:
    DEVELOPMENT_SERVER_HOST = '127.0.0.1'
try:
    DEVELOPMENT_SERVER_PORT = app.config['DEVELOPMENT_SERVER_PORT']
except KeyError:
    DEVELOPMENT_SERVER_PORT = 5000

# Create a Server object.
server = Server(host=DEVELOPMENT_SERVER_HOST, port=DEVELOPMENT_SERVER_PORT)

# Add command for running the server.
manager.add_command('runserver', server)

if __name__ == '__main__':
    # Run the manager.
    manager.run()