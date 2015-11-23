# views.py
# Jake Malley
# Views for the student blueprint.

# Flask Imports
from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.login import current_user
from flask.ext.mail import Message
# Application Imports
from peri2organise import db
from peri2organise import mail
from peri2organise.models import User
from peri2organise.auth.utils import login_required
from peri2organise.student.forms import UpdatePersonalDetailsForm
from peri2organise.student.forms import ContactForm
from peri2organise.student.utils import select_future_lessons
from peri2organise.student.utils import select_past_lessons
from peri2organise.student.utils import select_lessons_assoc
from peri2organise.student.utils import select_user
from peri2organise.student.utils import select_users_by_role
from peri2organise.student.utils import select_users_by_roles
# Imports
from datetime import datetime

# Create student blueprint
student_blueprint = Blueprint('student', __name__)

@student_blueprint.route('/dashboard')
@login_required(role="STU")
def dashboard():
    """
    Student Dashboard.
    """
    # Get the current time.
    now = datetime.now()
    # Select the future lessons.
    future_lessons = select_future_lessons(current_user)
    # Select all the past lessons, that were attended. (Limit to 5)
    attended_lessons_assoc = select_lessons_assoc(
        current_user,
        max_date=now,
        attendance_codes=('A', 'L'),
        limit=5
    )
    # Select all the past lessons, that have not been recorded.
    unknown_lessons_assoc = select_lessons_assoc(current_user, max_date=now, attendance_code=None)
    # Render the dashboard template, passing in the lessons selected from the database.
    return render_template(
        'student/dashboard.html', lessons=future_lessons,
        attended_lessons_assoc=attended_lessons_assoc, unknown_lessons_assoc=unknown_lessons_assoc
    )

@student_blueprint.route('/lessons')
@login_required(role="STU")
def lessons():
    """
    All Lessons.
    """
    # Select all the lessons, where the student is the current user, and the lessons
    # are in the future.
    upcoming_lessons = select_future_lessons(current_user)
    # Select all previous lessons, where the student is the current user, and the lessons
    # are in the past.
    previous_lessons = select_past_lessons(current_user)
    # Render the template passing in the lessons selected from the database.
    return render_template(
        'student/lessons.html', upcoming_lessons=upcoming_lessons, previous_lessons=previous_lessons
    )

@student_blueprint.route('/lessons/<int:lesson_id>')
@login_required(role="STU")
def view_lesson(lesson_id):
    """
    View a single Lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    assoc = select_lessons_assoc(current_user, lesson_id=lesson_id)
    # Ensure the assoc exists.
    if assoc:
        assoc = assoc[0]
    else:
        # Abort with 404 error code.
        abort(404)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'student/view_lesson.html', lesson=assoc.lesson, assoc=assoc
    )

@student_blueprint.route('/tutors')
@login_required(role='STU')
def tutors():
    """
    All Tutors.
    """
    # Select all of the tutors from the database.
    all_tutors = select_users_by_role('TUT')
    # Render the tutors template, passing in the tutors.
    return render_template(
        'student/tutors.html', tutors=all_tutors
    )

@student_blueprint.route('/tutors/<int:tutor_id>')
@login_required(role='STU')
def view_tutor(tutor_id):
    """
    View Tutor.
    """
    # Select the tutor with the given tutor_id.
    tutor = select_user(tutor_id, role='TUT')
    # Render the template passing in the tutor object.
    return render_template(
        'student/view_tutor.html', tutor=tutor
    )

@student_blueprint.route('/staff')
@login_required(role='STU')
def staff():
    """
    All Staff.
    """
    # Select all of the staff members.
    all_staff = select_users_by_role('STA')
    # Render the template passing in the staff members.
    return render_template(
        'student/staff.html', staff=all_staff)

@student_blueprint.route('/staff/<int:staff_id>')
@login_required(role='STU')
def view_staff(staff_id):
    """
    View Staff Member.
    """
    # Select the staff member with the given staff_id.
    staff_member = select_user(staff_id, role='STA')
    # Render the template passing in the staff member.
    return render_template(
        'student/view_staff.html', staff_member=staff_member
    )

@student_blueprint.route('/attendance')
@login_required(role='STU')
def attendance():
    """
    View Attendance.
    """
    # Get the current year.
    year = datetime.now().year
    # Create a datetime object for the 1st Jan this year.
    beginning_of_year = datetime(year, 1, 1)

    # All attended.
    lessons_attended_assoc = select_lessons_assoc(
        current_user, min_date=beginning_of_year, attendance_code='A'
    )
    # All absent.
    lessons_absent_assoc = select_lessons_assoc(
        current_user, min_date=beginning_of_year, attendance_codes=('P', 'N')
    )
    # All late.
    lessons_late_assoc = select_lessons_assoc(
        current_user, min_date=beginning_of_year, attendance_code='L'
    )

    # Calculate percentages of attendance.
    # Total number of lessons.
    total_number_of_lessons = len(lessons_attended_assoc) + \
        len(lessons_absent_assoc)+len(lessons_late_assoc)
    # Ensure the total number of lessons is greater than zero,
    # in order to stop division by zero error.
    if total_number_of_lessons > 0:
        # Number present, Number Absent, Number Late.
        attendance_statistics = [
            len(lessons_attended_assoc)*100/total_number_of_lessons,
            len(lessons_absent_assoc)*100/total_number_of_lessons,
            len(lessons_late_assoc)*100/total_number_of_lessons
        ]
    else:
        # All statistics will be zero.
        attendance_statistics = [0, 0, 0]
    # Render the template passing all of the data selected from the database.
    return render_template(
        'student/attendance.html', lessons_attended_assoc=lessons_attended_assoc,
        lessons_late_assoc=lessons_late_assoc, lessons_absent_assoc=lessons_absent_assoc,
        attendance_statistics=attendance_statistics
    )

@student_blueprint.route('/personaldetails', methods=['GET', 'POST'])
@login_required(role='STU')
def personal_details():

    # Create the form object, for updating details.
    update_personal_details_form = UpdatePersonalDetailsForm()

    if request.method == 'POST' and update_personal_details_form.validate_on_submit():
        # Form is valid.
        # Ensure the update box is checked.
        if update_personal_details_form.update_details.data:
            # Update all the details.
            current_user.update_user_details(
                first_name=update_personal_details_form.student_first_name.data,
                last_name=update_personal_details_form.student_last_name.data,
                email_address=update_personal_details_form.student_email_address.data,
                tutor_group=update_personal_details_form.student_tutor_group.data,
                musical_instrument_type=update_personal_details_form.musical_instrument_type.data,
                musical_instrument=update_personal_details_form.musical_instrument.data,
                musical_style=update_personal_details_form.musical_style.data,
                musical_grade=update_personal_details_form.musical_grade.data
            )
            # Save the changes.
            db.session.commit()
            # Flash a success method.
            flash('Successfully updated personal details.')
            # Redirect to this page - some weird stuff was happening with get_personal_details
            return redirect(url_for('student.personal_details'))

    # Create a dictionary of the required personal details.
    user_personal_details = current_user.get_personal_details()
    # Change the defaults in the form - for select boxes only!
    update_personal_details_form.musical_instrument_type.default = \
        personal_details['musical_instrument_type']
    update_personal_details_form.musical_style.default = \
        personal_details['musical_style']
    update_personal_details_form.musical_grade.default = \
        personal_details['musical_grade']
    # Update the form to reflect changes.
    update_personal_details_form.process()

    return render_template(
        'student/personaldetails.html',
        update_personal_details_form=update_personal_details_form,
        personal_details=user_personal_details
    )

@student_blueprint.route('/contact', methods=['GET', 'POST'])
@login_required(role='STU')
def contact():

    # Create an empty error.
    error = None

    # Create a form object.
    contact_form = ContactForm()

    # Select all the staff and tutors.
    contact_form.user.choices = [
        (user.user_id, user.get_full_name()) for user in select_users_by_roles(('TUT', 'STA'))
    ]

    if request.method == 'POST' and contact_form.validate_on_submit():
        # Form is valid.
        # Check the staff members is not the default
        if contact_form.user.data == '0':
            error = 'A staff member must be chosen.'
        else:
            # Find the user.
            user = User.query.filter(User.user_id == contact_form.user.data).first()
            # Create a new email message.
            message = Message(contact_form.subject.data, recipients=[user.get_email_address()])
            # Assign the message html to the rendered message template.
            message.html = render_template(
                'email/message.html', user=user, subject=contact_form.subject.data,
                message=contact_form.message.data
            )
            # Send the message.
            mail.send(message)
            # Flash a success message.
            flash('Successfully sent message.')
            # Redirect to the dashboard.
            return redirect(url_for('student.dashboard'))

    return render_template('student/contact.html', contact_form=contact_form, error=error)
