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
from flask.ext.mail import Message
# Application Imports
from peri2organise import app
from peri2organise import db
from peri2organise import mail
from peri2organise.auth.forms import LoginForm
from peri2organise.auth.forms import RegistrationForm
from peri2organise.auth.forms import GetEmailAddressForm
from peri2organise.auth.forms import ResetPasswordForm
from peri2organise.auth.forms import ChangePasswordForm
from peri2organise.auth.utils import login_required
from peri2organise.auth.utils import get_current_user_dashboard
from peri2organise.auth.utils import timed_safe_url_dump
from peri2organise.auth.utils import timed_safe_url_load
from peri2organise.models import User
from peri2organise.models import Parent


# Create auth blueprint.
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login to the application.
    """

    # Set empty error.
    error = None

    # Create a login form object.
    login_form = LoginForm()

    # If the current user is logged in.
    if current_user.is_authenticated:
        return redirect(get_current_user_dashboard())

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
                    return redirect(get_current_user_dashboard())
            else:
                # User could not be logged in, check the account is active.
                if user.is_active():
                    error = "Unknown error occurred, please contact your system administrator."
                else:
                    error = "Your account is not active, please contact your system administrator."
        else:
            error = "Invalid credentials."

    return render_template('auth/login.html', error=error, login_form=login_form)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register for the application.
    """

    # Set empty error.
    error = None

    # Create a registration form object.
    registration_form = RegistrationForm()
    # Create a login form object (for the nav bar form).
    login_form = LoginForm()

    if request.method == 'POST' and registration_form.validate_on_submit():
        # Form is valid.
        # Check there isn't already a user with this email address.
        user = User.query.filter_by(
            email_address=registration_form.student_email_address.data
        ).first()
        if  user is not None:
            error = "A user is already associated with this email address."
            return render_template(
                'auth/register.html', error=error,
                registration_form=registration_form, login_form=login_form
            )
        # Check there isn't already a parent with these details.
        parent = Parent.query.filter_by(
            email_address=registration_form.parent_email_address.data
        ).first()
        # If the parent exists.
        if parent is not None:
            # Parent already exists, lets use there details.
            # But check the phone number also matches.
            if parent.get_telephone_number() != registration_form.parent_telephone_number.data:
                error = "A parent is already associated with this email address, \
                    but could not be added to this student as the telephone number \
                    provided did not match. Please either use a different email address \
                    or the same telephone number as previously used."

                return render_template(
                    'auth/register.html', error=error,
                    registration_form=registration_form, login_form=login_form
                )
            else:
                # If the telephone number matched, use this parent's ID.
                parent_id = parent.parent_id
        else:
            # Add new parent.
            new_parent = Parent()
            # Update the new parent's details.
            new_parent.update_parent_details(
                first_name=registration_form.parent_first_name.data,
                last_name=registration_form.parent_last_name.data,
                email_address=registration_form.parent_email_address.data,
                telephone_number=registration_form.parent_telephone_number.data
            )
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

        # If the user selected a musical instrument type of singing set instrument to voice.
        if registration_form.musical_instrument.data == 'singing':
            new_user_musical_instrument = 'Voice'
        else:
            new_user_musical_instrument = registration_form.musical_instrument.data

        # Update the new user's details
        new_user.update_user_details(
            first_name=registration_form.student_first_name.data,
            last_name=registration_form.student_last_name.data,
            email_address=registration_form.student_email_address.data,
            role='STU',
            tutor_group=registration_form.student_tutor_group.data,
            musical_instrument_type=registration_form.musical_instrument_type.data,
            musical_instrument=new_user_musical_instrument,
            musical_style=registration_form.musical_style.data,
            musical_grade=int(registration_form.musical_grade.data),
            lesson_type=registration_form.lesson_type.data,
            lesson_pairing=registration_form.lesson_pairing.data,
            password=password_hash,
            parent_id=parent_id
        )
        # Add the new user to the database.
        db.session.add(new_user)
        # Commit changes to the database.
        db.session.commit()
        # Flash a success message.
        flash("Successfully added new user.", "info")
        # Redirect them to the login page.
        return redirect(url_for('auth.login'))

    return render_template(
        'auth/register.html',
        error=error,
        registration_form=registration_form,
        login_form=login_form
    )

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

@auth_blueprint.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    """
    Generate a forgot password token and email to user.
    """

    # Set empty error.
    error = None

    # Create a new form object.
    get_email_address_form = GetEmailAddressForm()

    if request.method == 'POST' and get_email_address_form.validate_on_submit():
        # If the request was a post and the form was valid.
        # Find the user by email.
        user = User.query.filter(
            User.email_address == get_email_address_form.email_address.data
        ).first()
        # Ensure the user exists.
        if user is not None:
            # Create an array of data to serialize.
            data = [user.get_first_name(), user.get_email_address(), user.password]
            # Create a timed safe url.
            dump = timed_safe_url_dump(data, salt='password_reset_form')
            # Create an email message.
            message = Message('Password Reset', recipients=[user.get_email_address()])
            message.html = render_template(
                'email/forgotpassword.html', name=user.get_first_name(),
                link=url_for('auth.reset_password', _external=True, token=dump)
            )
            # Send the message.
            mail.send(message)
            # Flash a success message.
            flash('Successfully sent reset email.')
            # Redirect to the homepage.
            return redirect(url_for('home.index'))
        else:
            error = 'Invalid E-Mail address.'
            flash(error, 'error')

    return render_template(
        'auth/forgotpassword.html',
        get_email_address_form=get_email_address_form, error=error
    )

@auth_blueprint.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    """
    Reset user's password.
    """

    # Set an empty error.
    error = None

    # Create a reset password form object.
    reset_password_form = ResetPasswordForm()

    # Check the method is POST and the form is valid.
    if request.method == 'POST' and reset_password_form.validate_on_submit():

        # Get the token.
        token = request.args.get('token')
        if not token:
            # If the token wasn't given in the url, create this error message.
            error = "Password reset token not provided, try copying and pasting \
                the link from your password reset email. Or return to the homepage."
        else:
            # Decode the token.
            data = timed_safe_url_load(
                token, app.config['MAX_PASSWORD_TOKEN_AGE'],
                salt='password_reset_form'
            )
            # If the decode function returned false.
            if not data:
                # Invalid token error.
                error = "Invalid reset token, try copying and pasting the link \
                from your password reset email. Or return to the homepage."
            else:
                # Proceed with the reset.
                # Find the user.
                user = User.query.filter(User.email_address == data[1]).first()
                # Check the password hash matches.
                if data[2] == user.password:
                    # Reset the password, with the new password.
                    new_password = user.create_password_hash(reset_password_form.password.data)
                    # Update the user's details.
                    user.update_user_details(password=new_password)
                    # Commit the changes.
                    db.session.commit()
                    # Flash a success message.
                    flash("Password successfully updated.")
                    # Redirect the user to the login page.
                    return redirect(url_for('auth.login'))
                else:
                    error = "Invalid reset token, try copying and pasting the link \
                        from your password reset email. Or return to the homepage."

    return render_template(
        'auth/resetpassword.html',
        error=error, reset_password_form=reset_password_form
    )

@auth_blueprint.route('/changepassword', methods=['GET', 'POST'])
@login_required()
def change_password():
    """
    Change current user's password.
    """   

    # Set an empty error.
    error = None

    # Create a reset password form object.
    change_password_form = ChangePasswordForm()

    # Check the method is POST and the form is valid.
    if request.method == 'POST' and change_password_form.validate_on_submit():

        # Check to ensure the current password is correct.
        if not current_user.check_password_hash(change_password_form.current_password.data):
            # Incorrect password.
            error = "The current password you entered is incorrect."
        else:
            # Reset their password.
            password_hash = current_user.create_password_hash(
                change_password_form.new_password.data
            )
            # Update their details.
            current_user.update_user_details(
                password=password_hash
            )
            # Commit changes
            db.session.commit()
            # Flash Success message.
            flash("Successfully changed password.")
            # Redirect home.
            return redirect(url_for('home.index'))

    return render_template(
        'auth/change_password.html',
        error=error, change_password_form=change_password_form
    )
