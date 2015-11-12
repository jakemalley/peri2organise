# utils.py
# Jake Malley
# Utilities for the student blueprint.

# Application Imports
from peri2organise.models import Lesson
from peri2organise.models import User
from peri2organise.models import UserLessonAssociation
# Imports
from datetime import datetime

def select_future_lessons(user_obj):
    """
    Query the database and select lessons in
    the future, belonging to the user = user_obj.
    """
    # Get the current time.
    now = datetime.now()
    # Select all the lesson objects, which belong
    # to the user_obj and have a time > now.
    return Lesson.query.filter(Lesson.users.contains(user_obj)).filter(Lesson.lesson_datetime>now).all()

def select_past_lessons(user_obj):
    """
    Query the database and select lessons in the
    past, for the user = user_obj.
    """
    # Get the current time.
    now = datetime.now()
    # Select all the lesson objects, which belong
    # to the user_obj and have a time < now.
    return Lesson.query.filter(Lesson.users.contains(user_obj)).filter(Lesson.lesson_datetime<now).all()


def select_lessons_assoc(user_obj, **kwargs):
    """
    Query the database and select
    UserLessonAssociations, for the given user_obj and attendance_code.
    """
    # Create a base query.
    base_query = UserLessonAssociation.query.filter(UserLessonAssociation.user==user_obj)
    # Check if the lesson_id is set.
    if 'lesson_id' in kwargs and kwargs['lesson_id']:
        # Filter for the given lesson_id.
        base_query = base_query.filter(Lesson.lesson_id==kwargs['lesson_id'])
    # Check if the minimum date is set.
    if 'min_date' in kwargs and kwargs['min_date']:
        # Filter after the given date.
        base_query = base_query.filter(Lesson.lesson_datetime>kwargs['min_date'])
    # Check if the maximum date is set.
    if 'max_date' in kwargs and kwargs['max_date']:
        # Filter before the given date.
        base_query = base_query.filter(Lesson.lesson_datetime<kwargs['max_date'])
    # Check if the attendance code was specified.
    if 'attendance_codes' in kwargs:
        base_query = base_query.filter(UserLessonAssociation.attendance_code.in_(kwargs['attendance_codes']))
    # Check if the attendance code was specified.
    if 'attendance_code' in kwargs:
        base_query = base_query.filter(UserLessonAssociation.attendance_code==kwargs['attendance_code'])
    # Check if the limit is set.
    if 'limit' in kwargs and kwargs['limit']:
        base_query = base_query.limit(5)
    # Return all the selected objects.
    return base_query.all()

def select_users_by_role(role):
    """
    Query the database and select all users with
    the role = role.
    """
    return User.query.filter(User.role==role)

def select_user(user_id, **kwargs):
    """
    Query the database and select the user with
    the user_id = user_id and filter by any other
    keyword arguments.
    """
    # Create a base query, filter by the user_id.
    base_query = User.query.filter(User.user_id==user_id)
    # Check if the role is set.
    if 'role' in kwargs and kwargs['role']:
        # Filter by role.
        base_query = base_query.filter(User.role==kwargs['role'])
    # Return the first result (As we are filtering by a unique id, this should be one anyway.)
    return base_query.first()

