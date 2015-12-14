# models.py
# Jake Malley
# Application Models.

# Imports
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from datetime import datetime
# Application Imports
from peri2organise import db
from peri2organise import bcrypt

# User Model
class User(db.Model):
    """
    Database model for users.
    """
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(60), nullable=False, unique=True)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_login_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    is_account_active = db.Column(db.Boolean, nullable=False, default=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(3), nullable=False)

    # Specific to Students
    tutor_group = db.Column(db.String(6))
    musical_instrument_type = db.Column(db.String(10))
    musical_instrument = db.Column(db.String(20))
    musical_style = db.Column(db.String(9))
    musical_grade = db.Column(db.Integer)
    lesson_type = db.Column(db.String(10))
    lesson_pairing = db.Column(db.String(40))

    parent_id = db.Column(db.Integer, db.ForeignKey('parent.parent_id'))

    # Specific to Tutors/Staff
    telephone_number = db.Column(db.String(11))
    speciality = db.Column(db.String(10))

    # Relationships
    lessons = relationship('Lesson', secondary='user_lesson_association')
    instruments = relationship('Instrument', backref='user')

    # Is authenticated variable used by flask-login.
    is_authenticated = True

    def __repr__(self):
        return '<User %s>' %(self.get_full_name())

    def is_active(self):
        """
        Used by flask login to determine whether the account is active.
        """
        return bool(self.is_account_active)

    def is_anonymous(self):
        """
        False, as anonymous users aren't supported.
        """
        return False

    def get_id(self):
        """
        Returns the User's id.
        """
        return self.user_id

    def get_role(self):
        """
        Returns the User's role.
        """
        return self.role.upper()

    def update_user_details(self, **kwargs):
        """
        Updates the User's details.
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def update_last_login(self):
        """
        Updates the last login date.
        """
        self.last_login_date = datetime.now()

    def activate_account(self):
        """
        Activates the User's account.
        """
        self.is_account_active = True

    def deactivate_account(self):
        """
        Deactivates the User's account.
        """
        self.is_account_active = False

    def check_password_hash(self, password):
        """
        Compare a given password with the hash stored.
        """
        return bcrypt.check_password_hash(self.password, password)

    def create_password_hash(self, password):
        """
        Create a password hash and return it to the user.
        """
        return bcrypt.generate_password_hash(password)

    def get_first_name(self):
        """
        Returns the User's first name, formatted as a title.
        """
        return self.first_name.title()

    def get_last_name(self):
        """
        Returns the User's first name, formatted as a title.
        """
        return self.last_name.title()

    def get_full_name(self):
        """
        Returns the User's full name, formatted as a title.
        """
        return (self.first_name+" "+self.last_name).title()

    def get_email_address(self):
        """
        Returns the User's email address.
        """
        return self.email_address

    def get_join_date(self, time_format='%d %b %G %H:%M'):
        """
        Returns the User's join date in the given format.
        """
        return self.join_date.strftime(time_format)

    def get_last_login_date(self, time_format='%d %b %G %H:%M'):
        """
        Returns the User's last login date in the given format.
        """
        return self.last_login_date.strftime(time_format)

    def get_tutor_group(self):
        """
        Returns the User's tutor group in a uppercase format.
        """
        return self.tutor_group.upper()

    def get_speciality(self):
        """
        Returns the User's specialty.
        """
        if self.speciality:
            return self.speciality.title()
        else:
            return 'Unknown'

    def get_telephone_number(self):
        """
        Returns the User's telephone number.
        """
        if self.telephone_number:
            return self.telephone_number
        else:
            return 'Unknown'

    def get_personal_details(self):
        """
        Returns a dictionary of all the user's details.
        """
        return self.__dict__

    def get_musical_instrument_type(self):
        """
        Returns the musical instrument type.
        """
        return self.musical_instrument_type.title()

    def get_musical_instrument(self):
        """
        Returns the musical instrument.
        """
        return self.musical_instrument.title()

    def get_musical_style(self):
        """
        Returns the musical style.
        """
        return self.musical_style.title()

    def get_musical_grade(self):
        """
        Returns the musical grade.
        """
        if self.musical_grade == '0':
            return 'Ungraded'
        else:
            return self.musical_grade

    def get_lesson_type(self):
        """
        Returns the lesson type.
        """
        return self.lesson_type.title()

    def get_lesson_pairing(self):
        """
        Returns the lesson pairing.
        """
        if self.lesson_type == 'individual':
            return 'Not Applicable'
        else:
            return self.lesson_pairing.title()

# Parent Model
class Parent(db.Model):
    """
    Database model for parents.
    """
    __tablename__ = 'parent'

    parent_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(60), nullable=False, unique=True)
    telephone_number = db.Column(db.String(11), nullable=False)

    users = relationship('User', backref='parent')

    def __repr__(self):
        return '<Parent %s>' %(self.get_full_name())

    def update_parent_details(self, **kwargs):
        """
        Updates the Parent's details.
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_first_name(self):
        """
        Returns the Parent's first name, formatted as a title.
        """
        return self.first_name.title()

    def get_last_name(self):
        """
        Returns the Parent's first name, formatted as a title.
        """
        return self.last_name.title()

    def get_full_name(self):
        """
        Returns the Parent's full name, formatted as a title.
        """
        return (self.first_name+" "+self.last_name).title()

    def get_email_address(self):
        """
        Returns the Parent's email address.
        """
        return self.email_address

    def get_telephone_number(self):
        """
        Returns the Parent's telephone number.
        """
        return self.telephone_number

# Lesson Model
class Lesson(db.Model):
    """
    Database model for Lessons.
    """

    __tablename__ = 'lesson'

    lesson_id = db.Column(db.Integer, primary_key=True)
    lesson_datetime = db.Column(db.DateTime, nullable=False)
    lesson_duration = db.Column(db.Integer, nullable=False)
    lesson_notes = db.Column(db.Text)
    attendance_recorded = db.Column(db.Boolean, default=False)

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))

    users = relationship('User', secondary='user_lesson_association')

    def __repr__(self):
        return '<Lesson %s>' %(self.get_lesson_date())

    def update_lesson_details(self, **kwargs):
        """
        Updates the Lesson's details.
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_lesson_date(self, time_format='%d %b %G %H:%M'):
        """
        Returns the Lesson's date in the given format.
        """
        return self.lesson_datetime.strftime(time_format)

    def get_lesson_duration(self):
        """
        Returns the Lesson's duration in minutes.
        """
        return int(self.lesson_duration/60)

    def get_lesson_notes(self):
        """
        Returns the Lesson's notes.
        """
        return self.lesson_notes

    def is_attendance_recorded(self):
        """
        Returns True if the attendance has been recorded
        or False if not.
        """
        return bool(self.attendance_recorded)

# Room Model
class Room(db.Model):
    """
    Database model for storing information about
    the room used for lessons.
    """

    __tablename__ = 'room'

    room_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(10), nullable=False)
    facilities = db.Column(db.Text)

    lessons = relationship('Lesson', backref='room')

    def __repr__(self):
        return '<Room %s>' %(self.get_location())

    def update_room_details(self, **kwargs):
        """
        Updates the Room's details.
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_location(self):
        """
        Returns the Room's location, formatted in uppercase.
        """
        return self.location.upper()

    def get_facilities(self):
        """
        Returns the Room's facilities.
        """
        return self.facilities

# Instrument Model
class Instrument(db.Model):
    """
    Database model for storing information about
    school instruments.
    """

    __tablename__ = 'instrument'

    instrument_id = db.Column(db.Integer, primary_key=True)
    instrument_name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __repr__(self):
        return '<Instrument %s>' %(self.get_instrument_name())

    def update_instrument_details(self, **kwargs):
        """
        Updates the Instrument's details.
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_instrument_name(self):
        """
        Returns the Instrument's name, formatted as a title.
        """
        return self.instrument_name.title()

    def get_description(self):
        """
        Returns the Instrument's description.
        """
        return self.description

# User Lesson Association Model
class UserLessonAssociation(db.Model):
    """
    Association table between User and Lesson.
    """

    __tablename__ = 'user_lesson_association'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'), primary_key=True)
    attendance_code = db.Column(db.String(1))
    attendance_notes = db.Column(db.Text)

    user = relationship(User, backref=backref('lesson_association'))
    lesson = relationship(Lesson, backref=backref('user_association'))

    def __repr__(self):
        return '<UserLessonAssociation (%s) and (%s)>' \
            %(self.user.__repr__(), self.lesson.__repr__())

    def get_lesson_attendance_str(self):
        """
        Return lesson attendance text.
        """
        if self.attendance_code == 'A':
            return 'Present'
        elif self.attendance_code == 'P':
            return 'Planned Absence'
        elif self.attendance_code == 'L':
            return 'Late'
        elif self.attendance_code == 'N':
            return 'Absent, No Reason Provided'
        else:
            return 'Not Recorded' 
