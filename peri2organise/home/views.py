# views.py
# Jake Malley
# Views for the home blueprint.

# Flask Imports
from flask import Blueprint
from flask import render_template
# Application Imports
from peri2organise.auth.forms import LoginForm

home_blueprint = Blueprint('home',__name__)

@home_blueprint.route('/')
def index():
    """
    Home Page.
    """
    # Create a login form object (for the nav bar form).
    login_form = LoginForm()

    return render_template('home/index.html',login_form=login_form)

@home_blueprint.route('/terms')
def terms():
    """
    Terms and Conditions page.
    """
    # Create a login form object (for the nav bar form).
    login_form = LoginForm()
    
    return render_template('home/terms.html',login_form=login_form)