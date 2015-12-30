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
        'parent first name', validators=[Optional(), Length(max=20)]
    )
    # Text field for the parent's last name.
    parent_last_name = TextField(
        'parent last name', validators=[Optional(), Length(max=20)]
    )
    # Text field for the parent's email address.
    parent_email_address = TextField(
        'parent email address', validators=[Optional(), Email(), Length(max=60)]
    )
    # Text field for the parent's telephone number.
    parent_telephone_number = TextField(
        'parent telephone number',
        validators=[Optional(), Length(
            message='Field must be exactly 11 characters.', min=11, max=11
        ), only_has_digits]
    )

    # Tutor/Staff specific
    # Text field for the user's speciality.
    speciality = TextField(
        'speciality', validators=[Optional(), Length(max=10)]
    )
    # Text field for the parent's telephone number.
    telephone_number = TextField(
        'telephone number',
        validators=[Optional(), Length(
            message='Field must be exactly 11 characters.', min=11, max=11
        ), only_has_digits]
    )

    def validate_optional_form_fields(self):
        """
        Validates the optional form fields based on the role.
        """
        # Set the return flag to true.
        # Check the user's role.
        flag = True
        if self.role.data == 'STU':
            # Required fields based on student requirements.
            required_fields = ['tutor_group', 'parent_first_name', 'parent_last_name', 'parent_email_address', 'parent_telephone_number']
            # Validate the lesson_pairing and musical_instrument fields.
            if self.musical_instrument_type.data == 'instrument':
                # The musical instrument field must be valid.
                if len(self.musical_instrument.data) <= 0:
                    self.musical_instrument.errors.append('This field is required.')
                    flag = False
            if self.lesson_type.data == 'paired':
                # The lesson pairing cannot be blank.
                if len(self.lesson_pairing.data) <= 0:
                    self.lesson_pairing.errors.append('This field is required.')
                    flag = False
                    
        else:
            # Required fields based on tutor requirements.
            required_fields = ['speciality', 'telephone_number']

        # Check the required fields are present.
        for field_name in required_fields:
            if field_name in self.data and len(self.data[field_name]) <= 0:
                getattr(self, field_name).errors.append('This field is required.')
                flag = False

        return flag