# views.py
# Jake Malley
# Views for the authentication blueprint.

# Flask Imports
from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user
# Application Imports
from peri2organise import db
from peri2organise.auth.forms import LoginForm
from peri2organise.auth.forms import  RegistrationForm
from peri2organise.auth.utils import login_required
from peri2organise.models import User
from peri2organise.models import Parent

# Create auth blueprint.
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET','POST'])
def login():

    # Set empty error. 
    error = None

    # Create a login form object.
    login_form = LoginForm()

    # If the current user is logged in.
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST' and login_form.validate_on_submit():
        # Form is valid.
        # Find the user.
        user = User.query.filter_by(email_address=login_form.email_address.data).first()
        if user is not None and user.check_password_hash(login_form.password.data):
            # The user is valid + password check passed.
            if login_user(user, remember=bool(login_form.remember_me.data)):
                # User has been logged in.
                flash("Successfully Authenticated.")
                # Update the last login date.
                user.update_last_login()
                # Commit those changes.
                db.session.commit()

                # Check if there are any 'next' arguments in the url.
                if request.args.get('next') and not request.args.get('next') == "/logout":
                    return redirect(request.args.get('next'))
                else:
                    # Redirect them to their dashboard page.
                    if user.get_role() == "STU":
                        # Student
                        return redirect(url_for('student.dashboard'))
                    elif user.get_role() == "STA":
                        # Staff
                        return redirect(url_for('staff.dashboard'))
                    elif user.get_role() == "TUT":
                        # Tutor
                        return redirect(url_for('tutor.dashboard'))
            else:
                # User could not be logged in, check the account is active.
                if user.is_active():
                    error = "Unknown error occurred, please contact your system administrator."
                else:
                    error = "Your account is not active, please contact your system administrator."
        else:
            error = "Invalid credentials."
        

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
        # Check there isn't already a user with this email address.
        if User.query.filter_by(email_address=registration_form.student_email_address.data).first() is not None:
            error = "A user is already associated with this email address."
            return render_template('auth/register.html', error=error, registration_form=registration_form,login_form=login_form)
        # Check there isn't already a parent with these details.
        parent = Parent.query.filter_by(email_address=registration_form.parent_email_address.data).first()
        if parent is not None:
            # Parent already exists, lets use there details.
            # But check the phone number also matches.
            if parent.get_telephone_number() != registration_form.parent_telephone_number.data:
                error = "A parent is already associated with this email address, but could not be added to this student as the telephone number provided did not match. Please either use a different email address or the same telephone number as previously used."
                return render_template('auth/register.html', error=error, registration_form=registration_form,login_form=login_form)
            else:
                # If the telephone number matched, use this parent's ID.
                parent_id = parent.parent_id
        else:
            # Add new parent.
            new_parent = Parent()
            # Update the new parent's details.
            new_parent.update_parent_details(first_name=registration_form.parent_first_name.data, last_name=registration_form.parent_last_name.data, email_address=registration_form.parent_email_address.data,telephone_number=registration_form.parent_telephone_number.data)
            # Add the new parent to the database.
            db.session.add(new_parent)
            # Commit the changes to the database.
            db.session.commit()
            # Get the parent_id.
            parent_id = new_parent.parent_id

        # Add the new user.
        new_user = User()
        # Create a password hash.
        password_hash = new_user.create_password_hash(registration_form.password.data)
        # Update the new user's details
        new_user.update_user_details(first_name=registration_form.student_first_name.data,last_name=registration_form.student_last_name.data,email_address=registration_form.student_email_address.data,role='STU',tutor_group=registration_form.student_tutor_group.data,musical_instrument_type=registration_form.musical_instrument_type.data,musical_instrument=registration_form.musical_instrument.data,musical_style=registration_form.musical_style.data,musical_grade=int(registration_form.musical_grade.data),lesson_type=registration_form.lesson_type.data,lesson_pairing=registration_form.lesson_pairing.data,password=password_hash,parent_id=parent_id)
        # Add the new user to the database.
        db.session.add(new_user)
        # Commit changes to the database.
        db.session.commit()
        # Flash a success message.
        flash("Successfully added new user.","info")
        # Redirect them to the login page.
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', error=error, registration_form=registration_form,login_form=login_form)

@auth_blueprint.route('/logout')
@login_required()
def logout():
    """
    Logout the currently logged in user.
    """
    # Logout the user.
    logout_user()
    # Flash a message.
    flash("Successfully logged out.")
    # Redirect to the home page.
    return redirect(url_for('home.index'))