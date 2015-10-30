# utils.py
# Jake Malley
# Provides utilities to be used in the auth blueprint.

# Imports
from functools import wraps
# Flask Imports
from flask.ext.login import current_user
# Application imports
from peri2organise import app
from peri2organise import login_manager

def login_required(role="ANY"):
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
                return login_manager.unauthorized()
            return func(*args,**kwargs)
        return decorated_view
    return wrapper