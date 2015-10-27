# manage.py
# Jake Malley
# Uses flask-script to provide a management script.

# Flask Imports
from flask.ext.script import Manager
from flask.ext.script import Server
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand
# Application Imports
from peri2organise import app
from peri2organise import db
from peri2organise.models import Student, Parent, Tutor, Lesson, Room, Instrument, StudentLessonAssociation, LessonTutorAssociation

# Create a Manager object.
manager = Manager(app)
# Create a Migration object.
migrate = Migrate(app,db)

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
# Add migrate command to the manager.
manager.add_command('db', MigrateCommand)

# Command to create the database.
@manager.command
def create_db():
    """
    Command to create the database.

    Use this command to create the all the tables from the models in models.py.
    (Alternatively Flask-Migrate can be used.)
    """
    db.create_all()

if __name__ == '__main__':
    # Run the manager.
    manager.run()