# __init__.py
# Jake Malley
# Initialize application.

# Flask Imports
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
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
# Create login manager object.
login_manager = LoginManager()
login_manager.init_app(app)
# Flask Login Configuration
login_manager.login_view='auth.login'
login_manager.refresh_view='auth.login'
login_manager.needs_refresh_message = (u"To protect your account, please re authenticate to access this page.")

@login_manager.user_loader
def load_user(user_id):
    """
    Load User object with user_id equal to the given user_id.
    """
    return User.query.filter(User.user_id==user_ud).first()

# Import Blueprints
from peri2organise.home.views import home_blueprint
from peri2organise.auth.views import auth_blueprint

# Register Blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(auth_blueprint, url_prefix='/auth')
