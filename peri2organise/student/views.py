# views.py
# Jake Malley
# Views for the student blueprint.

# Flask Imports
from flask import Blueprint
from flask import render_template
from flask.ext.login import current_user
from peri2organise.auth.utils import login_required

# Create student blueprint
student_blueprint = Blueprint('student',__name__)

@student_blueprint.route('/dashboard')
@login_required(role="STU")
def dashboard():
    """
    Student Dashboard.
    """
    return render_template('student/dashboard.html')