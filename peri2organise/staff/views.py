# views.py
# Jake Malley
# Views used in the staff blueprint.

# Flask imports
from flask import Blueprint
# Application Imports
from peri2organise.auth.utils import login_required

# Create tutor blueprint.
staff_blueprint = Blueprint('staff',__name__)

@staff_blueprint.route('/dashboard')
@login_required(role="STA")
def dashboard():
    """
    Staff dashboard.
    """
    return "STAFF DASHBOARD"
    # TODO
