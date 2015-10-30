# views.py
# Jake Malley
# Views used in the tutor blueprint.

# Flask imports
from flask import Blueprint
# Application Imports
from peri2organise.auth.utils import login_required

# Create tutor blueprint.
tutor_blueprint = Blueprint('tutor',__name__)

@tutor_blueprint.route('/dashboard')
@login_required(role="TUT")
def dashboard():
    """
    Tutor dashboard.
    """
    return "TUTOR DASHBOARD"
    # TODO
