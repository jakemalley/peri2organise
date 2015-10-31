# views.py
# Jake Malley
# Views for the home blueprint.

# Flask Imports
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask.ext.login import current_user
# Application Imports
from peri2organise.auth.forms import LoginForm
from peri2organise.auth.utils import get_current_user_dashboard

home_blueprint = Blueprint('home',__name__)

@home_blueprint.route('/')
def index():
    """
    Home Page.
    """

    # Check the user is not already authenticated.
    if current_user.is_authenticated:
        return redirect(get_current_user_dashboard())

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