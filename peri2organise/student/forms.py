# forms.py
# Jake Malley
# Forms used in the student blueprint.

# Flask Imports
from flask_wtf import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms.validators import StopValidation
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
# Application Imports
from peri2organise.auth.utils import is_on_email_domain

class UpdatePersonalDetailsForm(Form):

    """
    Form for users to update their personal details.
    """

    # Check box to enable updating details.
    update_details = BooleanField('update details', validators=[DataRequired('To update details, check this box.')])
    # Text field for the student's first name.
    student_first_name = TextField('student first name',validators=[DataRequired(),Length(max=20)])
    # Text field for the student's last name.
    student_last_name = TextField('student last name',validators=[DataRequired(),Length(max=20)])
    # Text field for the student's email address.
    student_email_address = TextField('student email address',validators=[DataRequired(), Email(), Length(max=60),is_on_email_domain])
    # Text field for the student's tutor group.
    student_tutor_group = TextField('student tutor group',validators=[DataRequired(),Length(max=6)])
    # Select field for the musical instrument type.
    musical_instrument_type = SelectField('musical instrument type', 
        choices=[('instrument','Instrument'),('singing','Singing')]
    )
    # Text field for the musical instrument.
    musical_instrument = TextField('musical instrument', validators=[Length(max=20)])
    # Select field for the musical style.
    musical_style = SelectField('musical style', 
        choices=[('jazz','Jazz'),('pop','Pop'),('classic','Classic')]
    )
    # Select field for musical grade.
    musical_grade = SelectField('musical grade', 
        choices=[('0','Ungraded'),('1','Grade 1'),('2','Grade 2'),('3','Grade 3'),('4','Grade 4'),('5','Grade 5'),('6','Grade 6'),('7','Grade 7'),('8','Grade 8')]
    )

class ContactForm(Form):

    """
    Form for contacting tutors/staff members.
    """

    # Select field to select the recipient.
    user = SelectField('user', coerce=int, choices=[('0','Select a Staff Member')])
    # Text field for the message subject.
    subject = TextField('subject', validators=[DataRequired()])
    # Text area field for the message.
    message = TextAreaField('message', validators=[DataRequired()])

