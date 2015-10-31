# utils.py
# Jake Malley
# Provides utilities to be used in the auth blueprint.

# Imports
from functools import wraps
# Flask Imports
from flask import redirect
from flask import url_for
from flask import flash
from flask import request
from flask.ext.login import current_user
# Application imports
from peri2organise import app
from peri2organise import login_manager

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
    flash("You do not have the required privileges to access that page.","error")
    # Redirect the to the page the came from, or their dashboard.
    return redirect(request.referrer or get_current_user_dashboard())

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

            return func(*args,**kwargs)
        return decorated_view
    return wrapper
