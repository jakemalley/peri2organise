# forms.py
# Jake Malley
# Forms for the staff blueprint.

# Flask Imports
from flask_wtf import Form
from wtforms import BooleanField
from wtforms.validators import Optional

class FilterLessonsForm(Form):
    """
    Forms used to filter lessons by type, either past or future.
    """
    # Boolean Fields to filter by.
    include_future_lessons = BooleanField('include future lessons', validators=[Optional()], default=True)
    include_past_lessons = BooleanField('include past lessons', validators=[Optional()])
