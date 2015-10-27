# models.py
# Jake Malley
# Application Models.

# Imports
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from datetime import datetime
# Application Imports
from peri2organise import db

# Student Model
class Student(db.Model):
    """
    Database model for students.
    """
    __tablename__ = 'student'

    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(30), nullable=False, unique=True)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_login_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    is_account_active = db.Column(db.Boolean, nullable=False, default=True)
    password = db.Column(db.String(60), nullable=False)
    tutor_group = db.Column(db.String(6), nullable=False)
    musical_instrument_type = db.Column(db.String(10), nullable=False)
    musical_instrument = db.Column(db.String(20), nullable=False)
    musical_style = db.Column(db.String(9), nullable=False)
    musical_grade = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(10), nullable=False)
    lesson_pairing = db.Column(db.String(40))

    parent_id = db.Column(db.Integer, db.ForeignKey('parent.parent_id'))

    lessons = relationship('Lesson', secondary='student_lesson_association')
    instruments = relationship('Instrument', backref='Student')

    def update_student_details(self, **kwargs):
        """
        Updates the Student's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def update_last_login(self):
        """
        Updates the last login date.
        """
        self.last_login_date = datetime.now()

    def activate_account(self):
        """
        Activates a Student's account.
        """
        self.is_account_active = True

    def deactivate_account(self):
        """
        Deactivates a Student's account.
        """
        self.is_account_active = False

    def check_password_hash(self, password):
        """
        Compare a given password with the hash stored.
        """
        pass # TODO

    def get_first_name(self):
        """
        Returns the Student's first name, formatted as a title.
        """
        return self.first_name.title()

    def get_last_name(self):
        """
        Returns the Student's first name, formatted as a title.
        """
        return self.last_name.title()

    def get_full_name(self):
        """
        Returns the Student's full name, formatted as a title.
        """
        return (self.first_name+" "+self.last_name).title()

    def get_email_address(self):
        """
        Returns the Student's email address.
        """
        return self.email_address

    def get_join_date(self, time_format = '%d %b %G %H:%M'):
        """
        Returns the Student's join date in the given format.
        """
        return self.join_date.strftime(time_format)

    def get_last_login_date(self, time_format = '%d %b %G %H:%M'):
        """
        Returns the Student's last login date in the given format.
        """
        return self.last_login_date.strftime(time_format)

    def get_tutor_group(self):
        """
        Returns the Student's tutor group in a uppercase format.
        """
        return self.tutor_group.upper()

# Parent Model
class Parent(db.Model):
    """
    Database model for parents.
    """
    __tablename__ = 'parent'

    parent_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(30), nullable=False, unique=True)
    telephone_number = db.Column(db.String(11), nullable=False)

    students = relationship('Student', backref='parent')

    def update_parent_details(self, **kwargs):
        """
        Updates the Parent's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

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

# Tutor Model
class Tutor(db.Model):
    """
    Database model for tutors (staff and peripatetic tutors).
    """
    __tablename__ = 'tutor'

    tutor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    telephone_number = db.Column(db.String(11), nullable=False)
    email_address = db.Column(db.String(30), nullable=False, unique=True)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_login_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    is_account_active = db.Column(db.Boolean, nullable=False, default=True)
    password = db.Column(db.String(60), nullable=False)
    speciality = db.Column(db.String(10), nullable=False)
    staff_role = db.Column(db.String(5), nullable=False)

    lessons = relationship('Lesson', secondary='lesson_tutor_association')

    def update_tutor_details(self, **kwargs):
        """
        Updates the Tutor's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def update_last_login(self):
        """
        Updates the last login date.
        """
        self.last_login_date = datetime.now()

    def activate_account(self):
        """
        Activates a Tutor's account.
        """
        self.is_account_active = True

    def deactivate_account(self):
        """
        Deactivates a Tutor's account.
        """
        self.is_account_active = False

    def check_password_hash(self, password):
        """
        Compare a given password with the hash stored.
        """
        pass # TODO

    def get_first_name(self):
        """
        Returns the Tutor's first name, formatted as a title.
        """
        return self.first_name.title()

    def get_last_name(self):
        """
        Returns the Tutor's first name, formatted as a title.
        """
        return self.last_name.title()

    def get_full_name(self):
        """
        Returns the Tutor's full name, formatted as a title.
        """
        return (self.first_name+" "+self.last_name).title()

    def get_email_address(self):
        """
        Returns the Tutor's email address.
        """
        return self.email_address

    def get_join_date(self, time_format = '%d %b %G %H:%M'):
        """
        Returns the Tutor's join date in the given format.
        """
        return self.join_date.strftime(time_format)

    def get_last_login_date(self, time_format = '%d %b %G %H:%M'):
        """
        Returns the Tutor's last login date in the given format.
        """
        return self.last_login_date.strftime(time_format)

    def get_speciality(self):
        """
        Returns the Tutor's specialty.
        """
        return self.speciality.title()

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

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))

    students = relationship('Student', secondary='student_lesson_association')
    tutors = relationship('Tutor', secondary='lesson_tutor_association')


    def update_lesson_details(self, **kwargs):
        """
        Updates the Lesson's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def get_lesson_date(self, time_format = '%d %b %G %H:%M'):
        """
        Returns the Lesson's date in the given format.
        """
        return self.last_login_date.strftime(time_format)

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

    def update_room_details(self, **kwargs):
        """
        Updates the Room's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

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

    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))

    def update_instrument_details(self, **kwargs):
        """
        Updates the Instrument's details.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

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

# Student Lesson Association Model
class StudentLessonAssociation(db.Model):
    """
    Association table between Student and Lesson.
    """

    __tablename__ = 'student_lesson_association'

    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'), primary_key=True)
    attendance_code = db.Column(db.String(1))
    attendance_notes = db.Column(db.Text)

    student = relationship(Student, backref=backref('lesson_association'))
    lesson = relationship(Lesson, backref=backref('student_association'))

# Lesson Tutor Association Model
class LessonTutorAssociation(db.Model):
    """
    Association table between Lesson and Tutor
    """

    __tablename__ = 'lesson_tutor_association'

    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'), primary_key=True)

    tutor = relationship(Tutor, backref=backref('lesson_association'))
    lesson = relationship(Lesson, backref=backref('tutor_association'))





