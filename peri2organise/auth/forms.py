# forms.py
# Jake Malley
# Forms used in the auth blueprint.

# Flask Imports
from flask_wtf import Form
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
# Application Imports
from peri2organise.auth.utils import only_has_digits
from peri2organise.auth.utils import is_on_email_domain

class LoginForm(Form):

    """
    User Login Form, used to authenticate users to the application.
    """

    # Text field for the users email address.
    email_address = TextField(
        'email', validators=[DataRequired(), Email(), Length(max=60)]
    )

    # Password field for the users password.
    password = PasswordField(
        'password', validators=[DataRequired(), Length(min=4, max=32)]
    )

    # Remember Me field.
    remember_me = BooleanField('remember me')

class RegistrationForm(Form):

    """
    User registration form, used to register students to the application.
    """

    # Student Details

    # Text field for the student's first name.
    student_first_name = TextField(
        'student first name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the student's last name.
    student_last_name = TextField(
        'student last name', validators=[DataRequired(), Length(max=20)]
    )
    # Text field for the student's email address.
    student_email_address = TextField(
        'student email address',
        validators=[DataRequired(), Email(), Length(max=60), is_on_email_domain]
    )
    # Password field for the student's password.
    password = PasswordField(
        'password', validators=[DataRequired(), Length(min=4, max=32)]
    )
    # Password confirm field for the student's password.
    password_confirm = PasswordField(
        'password confirm',
        validators=[
            EqualTo('password', message='Passwords must match.'),
            DataRequired(), Length(min=4, max=32)
        ]
    )
    # Text field for the student's tutor group.
    student_tutor_group = TextField(
        'student tutor group', validators=[DataRequired(), Length(max=6)]
    )
    # Select field for the musical instrument type.
    musical_instrument_type = SelectField(
        'musical instrument type',
        choices=[('instrument', 'Instrument'), ('singing', 'Singing')]
    )
    # Text field for the musical instrument.
    musical_instrument = TextField('musical instrument', validators=[Length(max=20)])
    # Select field for the musical style.
    musical_style = SelectField(
        'musical style',
        choices=[('jazz', 'Jazz'), ('pop', 'Pop'), ('classic', 'Classic')]
    )
    # Select field for musical grade.
    musical_grade = SelectField(
        'musical grade',
        choices=[
            ('0', 'Ungraded'), ('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'),
            ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'), ('7', 'Grade 7'), ('8', 'Grade 8')
        ]
    )
    # Select field for lesson type.
    lesson_type = SelectField(
        'lesson type',
        choices=[('individual', 'Individual'), ('paired', 'Paired')]
    )
    # Text field for lesson pairing.
    lesson_pairing = TextField('lesson_pairing', validators=[Length(max=40)])
    # Student signature.
    student_signature = BooleanField(
        'student signature',
        validators=[DataRequired('You must check this box to say that you \
            agree to the terms and conditions.')]
    )

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
    parent_signature = BooleanField(
        'parent signature',
        validators=[DataRequired('You must check this box to say that you \
            agree to the terms and conditions.')]
    )

class GetEmailAddressForm(Form):

    """
    Get email address form, used to for users to initiate a password reset.
    """

    # Text field for the users email address.
    email_address = TextField('email', validators=[DataRequired(), Email(), Length(max=60)])

class ResetPasswordForm(Form):

    """
    Reset password form, uses by users to reset their password.
    """

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

class ChangePasswordForm(Form):
    """
    Form for users to change their password.
    """

    # Password field for the user's password.
    current_password = PasswordField(
        'current password', validators=[DataRequired(), Length(min=4, max=32)]
    )

    # Password field for the user's password.
    new_password = PasswordField(
        'password', validators=[DataRequired(), Length(min=4, max=32)]
    )
    # Password confirm field for the user's password.
    new_password_confirm = PasswordField(
        'password confirm',
        validators=[
            EqualTo('new_password', message='Passwords must match.'),
            DataRequired(), Length(min=4, max=32)
        ]
    )
