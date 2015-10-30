# views.py
# Jake Malley
# Views for the authentication blueprint.

# Flask Imports
from flask import Blueprint, render_template, request, flash
# Application Imports
from peri2organise.auth.forms import LoginForm, RegistrationForm

# Create auth blueprint.
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET','POST'])
def login():

    # Set empty error. 
    error = None

    # Create a login form object.
    login_form = LoginForm()

    if request.method == 'POST' and login_form.validate_on_submit():
        # Form is valid.
        # TODO - USER LOGIN
        pass
        

    return render_template('auth/login.html', error=error, login_form=login_form)

@auth_blueprint.route('/register', methods=['GET','POST'])
def register():

    # Set empty error. 
    error = None

    # Create a registration form object.
    registration_form = RegistrationForm()
    # Create a login form object (for the nav bar form).
    login_form = LoginForm()

    if request.method == 'POST' and registration_form.validate_on_submit():
        # Form is valid.
        # TODO - USER REGISTRATION
        pass

    return render_template('auth/register.html', error=error, registration_form=registration_form,login_form=login_form)