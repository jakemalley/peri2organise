# forms.py
# Jake Malley
# Forms for the staff blueprint.

# Flask Imports
from flask_wtf import Form
from wtforms import BooleanField
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms.validators import Optional
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import EqualTo
# Application Imports
from peri2organise.auth.utils import only_has_digits

class FilterLessonsForm(Form):
    """
    Forms used to filter lessons by type, either past or future.
    """
    # Boolean Fields to filter by.
    include_future_lessons = BooleanField('include future lessons', validators=[Optional()], default=True)
    include_past_lessons = BooleanField('include past lessons', validators=[Optional()])

class AddUserForm(Form):

    # Text field for the user's first name.
    first_name = TextField(
        'first name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the user's last name.
    last_name = TextField(
        'last name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the user's email address.
    email_address = TextField(
        'email address',
        validators=[DataRequired(), Email(), Length(max=60)]
    )
    # Select field for the musical instrument type.
    role = SelectField(
        'role',
        choices=[('STU', 'Student'), ('TUT', 'Tutor'), ('STA', 'Staff')]
    )
    # Password field for the user's password.
    password = PasswordField(
        'password', validators=[DataRequired(), Length(min=4, max=32)]
    )
    # Password confirm field for the user's password.
    password_confirm = PasswordField(
        'password confirm',
        validators=[
            EqualTo('password', message='Passwords must match.'),
            DataRequired(), Length(min=4, max=32)
        ]
    )

    # Student specific.
    # Text field for the user's tutor group.
    tutor_group = TextField(
        'tutor group', validators=[Optional(), Length(max=6)]
    )
    # Select field for the musical instrument type.
    musical_instrument_type = SelectField(
        'musical instrument type',
        choices=[('instrument', 'Instrument'), ('singing', 'Singing')],
        validators=[Optional()]
    )
    # Text field for the musical instrument.
    musical_instrument = TextField('musical instrument', validators=[Optional(), Length(max=20)])
    # Select field for the musical style.
    musical_style = SelectField(
        'musical style',
        choices=[('jazz', 'Jazz'), ('pop', 'Pop'), ('classic', 'Classic')],
        validators=[Optional()]
    )
    # Select field for musical grade.
    musical_grade = SelectField(
        'musical grade',
        choices=[
            ('0', 'Ungraded'), ('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'),
            ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'), ('7', 'Grade 7'), ('8', 'Grade 8')
        ],
        validators=[Optional()]
    )
    # Select field for lesson type.
    lesson_type = SelectField(
        'lesson type',
        choices=[('individual', 'Individual'), ('paired', 'Paired')],
        validators=[Optional()]
    )
    # Text field for lesson pairing.
    lesson_pairing = TextField('lesson_pairing', validators=[Optional(), Length(max=40)])
    
    # Parent Details
    # Text field for the parent's first name.
    parent_first_name = TextField(
        'parent first name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the parent's last name.
    parent_last_name = TextField(
        'parent last name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the parent's email address.
    parent_email_address = TextField(
        'parent email address', validators=[DataRequired(), Email(), Length(max=60)]
    )
    # Text field for the parent's telephone number.
    parent_telephone_number = TextField(
        'parent telephone number',
        validators=[DataRequired(), Length(max=11), only_has_digits]
    )

    # Tutor/Staff specific
    # Text field for the user's speciality.
    speciality = TextField(
        'speciality', validators=[Optional(), Length(max=10)]
    )
    # Text field for the parent's telephone number.
    telephone_number = TextField(
        'telephone number',
        validators=[Optional(), Length(max=11), only_has_digits]
    )
