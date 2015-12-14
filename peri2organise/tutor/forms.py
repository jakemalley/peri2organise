# forms.py
# Jake Malley
# Forms for the tutor blueprint.

# Flask Imports
from flask_wtf import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import BooleanField
from wtforms import HiddenField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional
from wtforms.validators import NoneOf
# Application Imports
from peri2organise.auth.utils import is_on_email_domain

class SelectMinMaxDateForm(Form):
    """
    Form used to get a date from the user.
    """
    # Date fields for minimum and maximum dates.
    min_date = DateField('date', format='%Y-%m-%d', validators=[DataRequired()])
    max_date = DateField('date', format='%Y-%m-%d', validators=[DataRequired()])

class UpdatePersonalDetailsForm(Form):

    """
    Form for tutors to update their personal details.
    """

    # Check box to enable updating details.
    update_details = BooleanField(
        'update details', validators=[DataRequired('To update details, check this box.')]
    )
    # Text field for the tutor's first name.
    tutor_first_name = TextField(
        'tutor first name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the tutor's last name.
    tutor_last_name = TextField(
        'tutor last name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the tutor's email address.
    tutor_email_address = TextField(
        'tutor email address', validators=[
            DataRequired(), Email(), Length(max=60)
        ]
    )
    telephone_number = TextField(
        'telephone number', validators=[DataRequired(), Length(max=11)]
    )
    # Text field for the tutor's phone number.
    telephone_number = TextField(
        'telephone number', validators=[DataRequired(), Length(max=11)]
    )
    # Text field for the tutor's speciality.
    speciality = TextField(
        'speciality', validators=[DataRequired(), Length(max=10)]
    )

class AddLessonForm(Form):
    """
    Form used to add a new lesson.
    """

    # Lesson Date.
    lesson_date = DateField('date', format='%Y-%m-%d')
    # Lesson Hour
    lesson_hour = IntegerField('hour', validators=[InputRequired(), NumberRange(min=0, max=24)])
    # Lesson Minute
    lesson_minute = IntegerField('minute', validators=[InputRequired(), NumberRange(min=0, max=60)])
    # Lesson Duration (Minutes)
    lesson_duration = IntegerField('duration', validators=[DataRequired(), NumberRange(min=0)])
    # Lesson Notes
    lesson_notes = TextAreaField('notes')
    # Lesson Room
    lesson_room_id = SelectField('room', validators=[DataRequired()], coerce=int, choices=[])
    # Users
    users = SelectMultipleField(
        'users', validators=[DataRequired()], coerce=int, choices=[]
    )

class EditLessonForm(Form):
    """
    Form used to edit lessons.
    """

    # Lesson Date.
    lesson_date = DateField('date', format='%Y-%m-%d')
    # Lesson Hour
    lesson_hour = IntegerField('hour', validators=[DataRequired(), NumberRange(min=0, max=24)])
    # Lesson Minute
    lesson_minute = IntegerField('minute', validators=[InputRequired(), NumberRange(min=0, max=60)])
    # Lesson Duration (Minutes)
    lesson_duration = IntegerField('duration', validators=[DataRequired(), NumberRange(min=0)])
    # Lesson Notes
    lesson_notes = TextAreaField('notes')
    # Lesson Room
    lesson_room_id = SelectField('room', validators=[DataRequired()], coerce=int, choices=[])
    # Users to add.
    add_users = SelectMultipleField(
        'add users', validators=[Optional()], coerce=int, choices=[]
    )
    # Users to remove.
    remove_users = SelectMultipleField(
        'remove users', validators=[Optional()], coerce=int, choices=[]
    )

class RecordSingleAttendanceForm(Form):

    # Attendance Code
    attendance_code = SelectField('attendance code', 
        choices=[
            ('0', 'Please Select One'),
            ('A', 'Present'),
            ('L', 'Late'),
            ('P', 'Planned Absence'),
            ('N', 'Absent, No Reason Provided.')
        ],
        validators=[DataRequired(), NoneOf('0')]
    ) 

    # Hidden Field for the user id.
    user_id = HiddenField("user id", validators=[DataRequired()])