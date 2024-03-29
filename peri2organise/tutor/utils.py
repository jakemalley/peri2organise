# utils.py
# Jake Malley
# Utils used throughout the tutor blueprint.

# Flask Imports
from flask import render_template
from flask import url_for
from flask.ext.mail import Message
# Application Imports
from peri2organise import mail
from peri2organise.models import Lesson
from peri2organise.models import Parent
from peri2organise.models import User
# Imports
from datetime import timedelta

def generate_timesheet(user_obj, min_date, max_date):
    """
    Generates a time sheet report for the current user.
    """
    # Select all lessons and return them.
    return Lesson.query.filter(Lesson.users.contains(user_obj)) \
        .filter(Lesson.lesson_datetime >= min_date) \
        .filter(Lesson.lesson_datetime <= max_date+timedelta(days=1)).all()

def total_time(lessons):
    """
    Iterates through a list of lessons and totals the time in seconds.
    """
    # Set total to zero.
    total = 0
    # Loop through all the lessons.
    for lesson in lessons:
        total += lesson.lesson_duration
    # Put the total into (hours,mins,seconds)
    # Calculate minutes/seconds.
    m, s = divmod(total, 60)
    # Calculate hours/minutes.
    h, m = divmod(m, 60)
    # Return an tuple.
    return (h, m, s)

def select_lessons(user_obj, **kwargs):
    """
    Selects all lessons for the user and apply the given filters.
    """
    # Create a base query.
    base_query = Lesson.query.filter(Lesson.users.contains(user_obj))

    # Check if lesson id is set.
    if 'lesson_id' in kwargs and kwargs['lesson_id']:
        # Filter based on lesson id.
        base_query = base_query.filter(Lesson.lesson_id == kwargs['lesson_id'])
    # Check if the attendance recorded flag is set.
    if 'attendance_recorded' in kwargs:
        # Filter for lessons where attendance is/is not recorded.
        base_query = base_query.filter(Lesson.attendance_recorded == kwargs['attendance_recorded'])
    # Check if the minimum date is set.
    if 'min_date' in kwargs and kwargs['min_date']:
        # Filter after the given date.
        base_query = base_query.filter(Lesson.lesson_datetime >= kwargs['min_date'])
    # Check if the maximum date is set.
    if 'max_date' in kwargs and kwargs['max_date']:
        # Filter before the given date.
        base_query = base_query.filter(
            Lesson.lesson_datetime <= kwargs['max_date'] + timedelta(days=1)
        )
    if 'order_by' in kwargs:
        # Order by the given value.
        base_query = base_query.order_by(kwargs['order_by'])

    # If single is set, return the first result, otherwise return all.
    if 'single' in kwargs and kwargs['single']:
        return base_query.first()
    else:
        return base_query.all()

def select_students(user_obj, **kwargs):
    """
    Select student objects from the database.
    """
    # Check for keyword arguments.
    if 'my_students' in kwargs and kwargs['my_students']:
        # (Filtering by students who have lessons with this tutor.)
        # Find lessons for this user.
        lessons = select_lessons(user_obj)
        # Create an empty list.
        students = []
        # Iterate through the lessons.
        for lesson in lessons:
            for user in lesson.users:
                # If this user is a student and not already in the list.
                if user.role == 'STU' and user not in students:
                    # Add the student.
                    students.append(user)
        # Return the students.
        return students
    else:
        # If not set, select all students.
        base_query = User.query.filter(User.role == 'STU')

    return base_query.all()

def select_parents(**kwargs):
    """
    Returns the parent.
    """
    # Create a base query.
    base_query = Parent.query
    # If the id present filter by it.
    if 'parent_id' in kwargs and kwargs['parent_id']:
        base_query = base_query.filter(Parent.parent_id == kwargs['parent_id'])

    # Check to see if single is set
    if 'single' in kwargs and kwargs['single']:
        # Return the first result.
        return base_query.first()
    else:
        # Return all results.
        return base_query.all()

def check_attendance_complete(lesson_obj):
    """
    Checks to see if all the attendance has be recorded for a lesson object.
    """
    for assoc in lesson_obj.user_association:
        if assoc.user.get_role() == 'STU':
            # Check to see if it has been set.
            if assoc.attendance_code is None:
                return False

    return True

def send_lesson_update(user_obj, update_html, view_lesson_link, **kwargs):
    """
    Sends a lesson update to the user/their parent.
    """

    recipients = [user_obj.get_email_address()]

    if 'parent' in kwargs and kwargs['parent']:
        recipients.append(user_obj.parent.get_email_address())

    message = Message('Something has been updated.', recipients=recipients)
    # Render the html.
    message.html = render_template(
        'email/update.html',
        message=update_html,
        view_lesson_link=view_lesson_link
    )

    # Send the mail.
    mail.send(message)