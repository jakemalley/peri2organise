# views.py
# Jake Malley
# Views for the student blueprint.

# Flask Imports
from flask import Blueprint
from flask import render_template
from flask.ext.login import current_user
# Application Imports
from peri2organise.models import User
from peri2organise.models import Lesson
from peri2organise.models import UserLessonAssociation
from peri2organise.auth.utils import login_required
from peri2organise.student.utils import select_future_lessons
from peri2organise.student.utils import select_past_lessons
from peri2organise.student.utils import select_lessons_assoc
from peri2organise.student.utils import select_user
from peri2organise.student.utils import select_users_by_role
# Imports
from datetime import datetime

# Create student blueprint
student_blueprint = Blueprint('student',__name__)

@student_blueprint.route('/dashboard')
@login_required(role="STU")
def dashboard():
    """
    Student Dashboard.
    """
    # Get the current time.
    now = datetime.now()
    # Select the future lessons.
    lessons = select_future_lessons(current_user)
    # Select all the past lessons, that were attended. (Limit to 5)
    attended_lessons_assoc = select_lessons_assoc(current_user, max_date=now,attendance_codes=('A','L'),limit=5) 
    # Select all the past lessons, that have not been recorded.
    unknown_lessons_assoc = select_lessons_assoc(current_user, max_date=now,attendance_code=None) 
    # Render the dashboard template, passing in the lessons selected from the database.
    return render_template('student/dashboard.html',lessons=lessons,attended_lessons_assoc=attended_lessons_assoc,unknown_lessons_assoc=unknown_lessons_assoc)

@student_blueprint.route('/lessons')
@login_required(role="STU")
def lessons():
    """
    All Lessons.
    """
    # Get the current time.
    now = datetime.now()
    # Select all the lessons, where the student is the current user, and the lessons
    # are in the future.
    upcoming_lessons = select_future_lessons(current_user)
    # Select all previous lessons, where the student is the current user, and the lessons
    # are in the past.
    previous_lessons = select_past_lessons(current_user)
    # Render the template passing in the lessons selected from the database.
    return render_template('student/lessons.html',upcoming_lessons=upcoming_lessons,previous_lessons=previous_lessons)

@student_blueprint.route('/lessons/<int:lesson_id>')
@login_required(role="STU")
def view_lesson(lesson_id):
    """
    View a single Lesson.
    """
    # Get the UserLessonAssociation for the current and the given lesson id. (So we can also display attendance etc.)
    assoc = select_lessons_assoc(current_user,lesson_id=lesson_id)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template('student/view_lesson.html',lesson=assoc.lesson,assoc=assoc)

@student_blueprint.route('/tutors')
@login_required(role='STU')
def tutors():
    """
    All Tutors.
    """
    # Select all of the tutors from the database.
    tutors = select_users_by_role('TUT')
    # Render the tutors template, passing in the tutors.
    return render_template('student/tutors.html',tutors=tutors)

@student_blueprint.route('/tutors/<int:tutor_id>')
@login_required(role='STU')
def view_tutor(tutor_id):
    """
    View Tutor.
    """
    # Select the tutor with the given tutor_id.
    tutor = select_user(tutor_id,role='TUT')
    # Render the template passing in the tutor object.
    return render_template('student/view_tutor.html',tutor=tutor)

@student_blueprint.route('/staff')
@login_required(role='STU')
def staff():
    """
    All Staff.
    """
    # Select all of the staff members.
    staff = select_users_by_role('STA')
    # Render the template passing in the staff members.
    return render_template('student/staff.html',staff=staff)

@student_blueprint.route('/staff/<int:staff_id>')
@login_required(role='STU')
def view_staff(staff_id):
    """
    View Staff Member.
    """
    # Select the staff member with the given staff_id.
    staff_member = select_user(staff_id, role='STA')
    # Render the template passing in the staff member.
    return render_template('student/view_staff.html',staff_member=staff_member)

@student_blueprint.route('/attendance')
@login_required(role='STU')
def attendance():
    """
    View Attendance.
    """
    # Get the current year.
    year = datetime.now().year
    # Create a datetime object for the 1st Jan this year.
    beginning_of_year = datetime(year,1,1)
    # Select all user lesson associations (After 1st Jan this year.)
    assoc_base_query = UserLessonAssociation.query.filter(UserLessonAssociation.user==current_user).filter(Lesson.lesson_datetime>beginning_of_year)

    # All attended.
    lessons_attended_assoc = select_lessons_assoc(current_user,min_date=beginning_of_year,attendance_code='A')
    # All absent.
    lessons_absent_assoc = select_lessons_assoc(current_user,min_date=beginning_of_year,attendance_codes=('P','N'))
    # All late.
    lessons_late_assoc = select_lessons_assoc(current_user,min_date=beginning_of_year,attendance_code='L')
    # Calculate percentages of attendance.
    # Total number of lessons.
    total_number_of_lessons = len(lessons_attended_assoc)+len(lessons_absent_assoc)+len(lessons_late_assoc)
    # Number present, Number Absent, Number Late.
    attendance_statistics = [len(lessons_attended_assoc)*100/total_number_of_lessons,len(lessons_absent_assoc)*100/total_number_of_lessons,len(lessons_late_assoc)*100/total_number_of_lessons]
    # Render the template passing all of the data selected from the database.
    return render_template('student/attendance.html', lessons_attended_assoc=lessons_attended_assoc, lessons_late_assoc=lessons_late_assoc, lessons_absent_assoc=lessons_absent_assoc,attendance_statistics=attendance_statistics)