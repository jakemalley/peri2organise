# utils.py
# Jake Malley
# Provides utilities to be used in the auth blueprint.

# Imports
from functools import wraps
# Flask Imports
from flask import abort
from flask import url_for
from flask import flash
from flask.ext.login import current_user
from wtforms.validators import StopValidation
# Application imports
from peri2organise import app
from peri2organise import login_manager
# Imports
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature
from itsdangerous import BadData

def get_current_user_dashboard():
    """
    Returns a url_for object, for the current
    user's dashboard page.
    """
    # Redirect them to their dashboard page.
    if current_user.get_role() == "STU":
        # Student
        return url_for('student.dashboard')
    elif current_user.get_role() == "STA":
        # Staff
        return url_for('staff.dashboard')
    elif current_user.get_role() == "TUT":
        # Tutor
        return url_for('tutor.dashboard')

def unauthorized_role():
    """
    Informs a user they do not have the
    required role to view the requested
    page.
    """
    # Flash an error message to the user.
    flash("You do not have the required privileges to access that page.", "error")
    # Abort with 403 unauthorized error.
    abort(403)

def login_required(role="ANY"):
    """
    Login required decorator, capable of
    handling user roles.
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Ensure the current user is actually authenticated.
            if not current_user.is_authenticated:
                # The user is not authenticated.
                return login_manager.unauthorized()
            user_role = current_user.get_role()
            if user_role != role and role != "ANY":
                # The user doesn't have permission to be here.
                return unauthorized_role()

            return func(*args, **kwargs)
        return decorated_view
    return wrapper

def timed_safe_url_dump(data, salt='peri2organise'):
    """
    Serializes the data into a string, that is
    able to be used in URLs. Used for creating password reset token/
    authentication tokens.

    Salt can be used when generating safe URL tokens for different purposed,
    e.g. salt='reset_password' or salt='auth_token'.
    """

    try:
        secret_key = app.config['SECRET_KEY']
    except KeyError:
        raise Exception('A Secret Key is required to generate tokens.')
    else:
        # Ensure key is a string.
        if secret_key is None or isinstance(secret_key, str):
            raise Exception('A Secret Key is required to generate tokens.')

    # Create URL safe timed serializer.
    serializer = URLSafeTimedSerializer(secret_key, salt=salt)
    # Serialize the data.
    return serializer.dumps(data)

def timed_safe_url_load(serialized_data, max_age_in_seconds, salt='peri2organise'):
    """
    De-serializes the serialized data into the original data.

    Salt can be used when generating safe URL tokens for different purposed,
    e.g. salt='reset_password' or salt='auth_token'. The salt must be the same
    as the salt used when the data was serialized.
    """

    try:
        secret_key = app.config['SECRET_KEY']
    except KeyError:
        raise Exception('A Secret Key is required to generate tokens.')
    else:
        # Ensure key is a string.
        if secret_key is None or isinstance(secret_key, str):
            raise Exception('A Secret Key is required to generate tokens.')

    # Create URL safe timed serializer.
    serializer = URLSafeTimedSerializer(secret_key, salt=salt)

    try:
        # Try and decode the data.
        decoded_data = serializer.loads(serialized_data, max_age=max_age_in_seconds)
    except BadSignature, e:
        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                decoded_data = serializer.load_payload(encoded_payload)
            except BadData:
                return False
        return False
    else:
        return decoded_data

def is_on_email_domain(form, field):
    """
    Validator to ensure student's use their school email.
    """
    EMAIL_DOMAIN = app.config['EMAIL_DOMAIN']
    if field.data is not None:
        try:
            user, domain = field.data.split('@')
            if domain != EMAIL_DOMAIN:
                # Error message.
                field.errors.append('Email domain must be '+EMAIL_DOMAIN+'.')
                # Raise stop validation.
                raise StopValidation()
        except ValueError:
            # Error message.
            field.errors.append('Invalid email address.')
            # Raise stop validation.
            raise StopValidation()

def only_has_digits(form, field):
    """
    Validator to ensure a text field only contains digits.
    """
    if not field.data.isdigit():
        # Error message.
        field.errors.append('Field must only contain digits.')
        # Raise stop validation.
        raise StopValidation()
        