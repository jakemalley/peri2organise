# __init__.py
# Jake Malley
# Initialize application.

# Flask Imports
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
# Application Imports
from peri2organise.utils import load_application_configuration

# Create application object.
app = Flask(__name__)
# Load the configuration.
load_application_configuration(app)

# Create database object.
db = SQLAlchemy(app)
# Create bcrypt object, used for password hashing.
bcrypt = Bcrypt(app)
# Create mail object.
mail = Mail(app)
# Create login manager object.
login_manager = LoginManager()
login_manager.init_app(app)
# Flask Login Configuration
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = \
    (u"To protect your account, please re authenticate to access this page.")

# Import the error modules.
import peri2organise.error
# Import the admin module.
import peri2organise.admin

# Import the user model, for the user loader.
from peri2organise.models import User
@login_manager.user_loader
def load_user(user_id):
    """
    Load User object with user_id equal to the given user_id.
    """
    return User.query.filter(User.user_id == user_id).first()

# Import Blueprints
from peri2organise.home.views import home_blueprint
from peri2organise.auth.views import auth_blueprint
from peri2organise.student.views import student_blueprint
from peri2organise.staff.views import staff_blueprint
from peri2organise.tutor.views import tutor_blueprint

# Register Blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(student_blueprint, url_prefix='/student')
app.register_blueprint(staff_blueprint, url_prefix='/staff')
app.register_blueprint(tutor_blueprint, url_prefix='/tutor')
