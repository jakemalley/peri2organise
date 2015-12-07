# views.py
# Jake Malley
# Views used in the tutor blueprint.

# Flask imports
from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.login import current_user
from flask.ext.mail import Message
# Application Imports
from peri2organise import app
from peri2organise import db
from peri2organise import mail
from peri2organise.models import Lesson
from peri2organise.models import Parent
from peri2organise.models import Room
from peri2organise.models import User
from peri2organise.models import UserLessonAssociation
from peri2organise.auth.utils import login_required
from peri2organise.student.utils import select_future_lessons
from peri2organise.student.utils import select_past_lessons
from peri2organise.student.utils import select_lessons_assoc
from peri2organise.student.utils import select_user
from peri2organise.student.utils import select_users_by_roles
from peri2organise.student.forms import ContactForm
from peri2organise.tutor.forms import AddLessonForm
from peri2organise.tutor.forms import EditLessonForm
from peri2organise.tutor.forms import SelectMinMaxDateForm
from peri2organise.tutor.forms import RecordSingleAttendanceForm
from peri2organise.tutor.forms import UpdatePersonalDetailsForm
from peri2organise.tutor.utils import generate_timesheet
from peri2organise.tutor.utils import total_time
from peri2organise.tutor.utils import select_students
from peri2organise.tutor.utils import select_parents
from peri2organise.tutor.utils import select_lessons
from peri2organise.tutor.utils import check_attendance_complete
from peri2organise.tutor.utils import send_lesson_update
# Imports
from datetime import datetime
from datetime import time
from datetime import timedelta

# Create tutor blueprint.
tutor_blueprint = Blueprint('tutor', __name__)

@tutor_blueprint.route('/')
@login_required(role="TUT")
def index():
    """
    Index, redirect to dashboard.
    """
    return redirect(url_for('tutor.dashboard'))

@tutor_blueprint.route('/dashboard')
@login_required(role="TUT")
def dashboard():
    """
    Tutor dashboard.
    """
    return render_template(
        'tutor/dashboard.html'
    )

@tutor_blueprint.route('/lessons')
@login_required(role="TUT")
def lessons():
    """
    View all lessons.
    """
    # Select all the lessons, where the tutor is the current user, and the lessons
    # are in the future.
    upcoming_lessons = select_future_lessons(current_user)
    # Select all previous lessons, where the tutor is the current user, and the lessons
    # are in the past.
    previous_lessons = select_past_lessons(current_user)
    # Render the template passing in the lessons selected from the database.
    return render_template(
        'tutor/lessons.html', upcoming_lessons=upcoming_lessons, previous_lessons=previous_lessons
    )

@tutor_blueprint.route('/lessons/<int:lesson_id>')
@login_required(role="TUT")
def view_lesson(lesson_id):
    """
    View a single lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    assoc = select_lessons_assoc(current_user, lesson_id=lesson_id)

    # Ensure the lesson id/association object is found.
    if assoc:
        assoc = assoc[0]
    else:
        abort(404)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'tutor/view_lesson.html', lesson=assoc.lesson, assoc=assoc
    )

@tutor_blueprint.route('/lessons/add', methods=['GET', 'POST'])
@login_required(role="TUT")
def add_lesson():
    """
    Add a new lesson.
    """
    # Create empty error object.
    error = None

    # Create form.
    add_lesson_form = AddLessonForm()
    # Add the rooms.
    add_lesson_form.lesson_room_id.choices = [
        (room.room_id, room.get_location()) for room in Room.query.all()
    ]
    # Select all users.
    all_users = select_users_by_roles(('STU', 'TUT', 'STA'))
    # Update the form choices.
    add_lesson_form.users.choices = [
        (user.user_id, user.get_full_name()) for user in all_users
    ]
    # Remove the current user.
    add_lesson_form.users.choices.remove(
        (current_user.user_id, current_user.get_full_name())
    )

    if request.method == 'POST' and add_lesson_form.validate_on_submit():
        # Create a new lesson object.
        new_lesson = Lesson()
        # Create the datetime object.
        lesson_datetime = datetime.combine(
            add_lesson_form.lesson_date.data,
            time(
                add_lesson_form.lesson_hour.data,
                add_lesson_form.lesson_minute.data
            )
        )
        # Update the lesson details.
        new_lesson.update_lesson_details(
            lesson_datetime=lesson_datetime,
            lesson_duration=add_lesson_form.lesson_duration.data*60,
            lesson_notes=add_lesson_form.lesson_notes.data,
            room_id=add_lesson_form.lesson_room_id.data
        )
        # Iterate through the users.
        for user_id in add_lesson_form.users.data:
            # Select the user object.
            user_object = select_user(user_id)
            # Append it to the lessons users.
            new_lesson.users.append(user_object)

        # Add the current user to the lesson.
        new_lesson.users.append(current_user)

        # Flash a success message.
        flash("Successfully added new lesson.")

        # Add the lesson to the db.
        db.session.add(new_lesson)
        # Commit changes.
        db.session.commit()

        return redirect(url_for('tutor.add_lesson'))

    return render_template(
        'tutor/add_lesson.html', add_lesson_form=add_lesson_form, error=error
    )

@tutor_blueprint.route('/lessons/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required(role="TUT")
def edit_lesson(lesson_id):
    """
    Edit a lesson.
    """
    # Create a new edit lesson form.
    edit_lesson_form = EditLessonForm()
    # Add the rooms.
    edit_lesson_form.lesson_room_id.choices = [
        (room.room_id, room.get_location()) for room in Room.query.all()
    ]
    # Select all users.
    all_users = select_users_by_roles(('STU', 'TUT', 'STA'))
    # Set the choices for the users that can be selected for the new users.
    edit_lesson_form.add_users.choices = [
        (user.user_id, user.get_full_name()) for user in all_users
    ]
    # Remove the current user.
    edit_lesson_form.add_users.choices.remove(
        (current_user.user_id, current_user.get_full_name())
    )

    # Find the lesson with the given ID.
    lesson = select_lessons(current_user, lesson_id=lesson_id, single=True)

    # All the users that can be removed are the users of the lesson.
    edit_lesson_form.remove_users.choices = [
        (user.user_id, user.get_full_name()) for user in lesson.users
    ]
    # Remove the current user from these choices (as they must still be in the lesson).
    edit_lesson_form.remove_users.choices.remove(
        (current_user.user_id, current_user.get_full_name())
    )

    if request.method == 'POST' and edit_lesson_form.validate_on_submit():
        # Create the datetime object.
        lesson_datetime = datetime.combine(
            edit_lesson_form.lesson_date.data,
            time(
                edit_lesson_form.lesson_hour.data,
                edit_lesson_form.lesson_minute.data
            )
        )
        # Update the lesson.
        lesson.update_lesson_details(
            lesson_datetime=lesson_datetime,
            lesson_duration=edit_lesson_form.lesson_duration.data*60,
            lesson_notes=edit_lesson_form.lesson_notes.data,
            room_id=edit_lesson_form.lesson_room_id.data
        )

        # Iterate through the users to add.
        for user_id in edit_lesson_form.add_users.data:
            # Select the user object.
            user_object = select_user(user_id)
            # If the user is not already going to the lesson.
            if user_object not in lesson.users:
                # Append it to the lessons users.
                lesson.users.append(user_object)
        # Iterate through the users to remove.
        for user_id in edit_lesson_form.remove_users.data:
            # Delete the user lesson association for this user/lesson.
            db.session.delete(
                UserLessonAssociation.query.filter(
                    UserLessonAssociation.lesson_id == lesson_id
                ).filter(
                    UserLessonAssociation.user_id == user_id
                ).first()
            )

        # Commit Changes.
        db.session.commit()

        # Flash a success message.
        flash("Successfully updated lesson.")

    # Set the defaults.
    edit_lesson_form.lesson_date.default = lesson.lesson_datetime.date()
    edit_lesson_form.lesson_notes.default = lesson.get_lesson_notes()
    edit_lesson_form.lesson_room_id.default = lesson.room.room_id
    # Process the form.
    edit_lesson_form.process()

    return render_template(
        'tutor/edit_lesson.html', edit_lesson_form=edit_lesson_form, lesson=lesson
    )

@tutor_blueprint.route('/students')
@login_required(role="TUT")
def students():
    """
    View all students.
    """
    # Select the students.
    all_students = select_students(current_user, my_students=True)
    # Render the students template.
    return render_template(
        'tutor/students.html', students=all_students
    )

@tutor_blueprint.route('/students/<int:student_id>')
@login_required(role="TUT")
def view_student(student_id):
    """
    View a single student.
    """
    # Find the student.
    student = select_user(student_id, role='STU')
    # Check the user exists.
    if student is not None:
        return render_template(
            'tutor/view_student.html', student=student
        )
    else:
        # If the student isn't found, return a 404.
        abort(404)

@tutor_blueprint.route('/parents/<int:parent_id>')
@login_required(role="TUT")
def view_parent(parent_id):
    """
    View a single parent.
    """
    # Select the parent.
    parent = select_parents(parent_id=parent_id)
    # Check the parent exists.
    if parent is not None:
        return render_template(
            'tutor/view_parent.html', parent=parent[0]
        )
    else:
        # If the parent isn't found, return a 404.
        abort(404)

@tutor_blueprint.route('/attendance', methods=['GET', 'POST'])
@login_required(role="TUT")
def attendance():
    """
    Display all lessons attendance can be recorded for.
    """
    # Create new form objects for minimum and maximum dates.
    select_date_form = SelectMinMaxDateForm()

    if request.method == 'POST' and select_date_form.validate_on_submit():
        # Form was submitted and is valid, filter by dates.
        no_attendance_recorded = select_lessons(
            current_user, attendance_recorded=False,
            min_date=select_date_form.min_date.data, max_date=select_date_form.max_date.data
        )
    else:
        # Select all lessons with recorded attendance.
        no_attendance_recorded = select_lessons(current_user, attendance_recorded=False)

    # Render the attendance template.
    return render_template(
        'tutor/attendance.html',
        no_attendance_recorded=no_attendance_recorded,
        select_date_form=select_date_form
    )

@tutor_blueprint.route('/attendance/record/<int:lesson_id>', methods=['GET', 'POST'])
@login_required(role="TUT")
def record_attendance(lesson_id):
    """
    Record attendance for a lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    lesson = select_lessons(current_user, lesson_id=lesson_id, single=True)

    # Ensure the lesson id/association object is found.
    if not lesson:
        abort(404)

    record_single_attendance_form = RecordSingleAttendanceForm()

    if request.method == 'POST' and record_single_attendance_form.validate_on_submit():
        assoc = UserLessonAssociation.query.filter(
                UserLessonAssociation.lesson_id == lesson_id
            ).filter(
                UserLessonAssociation.user_id == int(record_single_attendance_form.user_id.data)
            ).first()

        if assoc:
            assoc.attendance_code = record_single_attendance_form.attendance_code.data
            flash("Successfully updated lesson attendance.")
        else:
            abort(500)

        if assoc.attendance_code == 'L' or assoc.attendance_code == 'N':
            # Send an email update.
            html = 'Attendance for your lesson on: ' + assoc.lesson.get_lesson_date() + ' has been updated. Your attendance is now recorded as: ' + assoc.get_lesson_attendance_str()
            send_lesson_update(assoc.user, html, parent=True)

        if check_attendance_complete(lesson):
            # The attendance is complete.
            lesson.update_lesson_details(attendance_recorded=True)
        else:
            lesson.update_lesson_details(attendance_recorded=False)

        # Save Changes
        db.session.commit()

        # Refresh
        return redirect(url_for('tutor.record_attendance', lesson_id=lesson_id))

    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'tutor/record_attendance.html', lesson=lesson,
        record_single_attendance_form=record_single_attendance_form
    )

@tutor_blueprint.route('/attendance/view/<int:lesson_id>')
@login_required(role="TUT")
def view_attendance(lesson_id):
    """
    View attendance for a lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    lesson = select_lessons(current_user, lesson_id=lesson_id, single=True)

    # Ensure the lesson id/association object is found.
    if not lesson:
        abort(404)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'tutor/view_attendance.html', lesson=lesson,
    )

@tutor_blueprint.route('/contact', methods=['GET', 'POST'])
@login_required(role="TUT")
def contact():
    """
    Contact student or staff member.
    """
    # Create an empty error.
    error = None

    # Create a form object.
    contact_form = ContactForm()

    # Select all the staff and tutors.
    contact_form.user.choices = [
        (user.user_id, user.get_full_name()) for user in select_users_by_roles(
            ('TUT', 'STA', 'STU')
        )
    ]

    if request.method == 'POST' and contact_form.validate_on_submit():
        # Form is valid.
        # Check the staff members is not the default
        if contact_form.user.data == '0':
            error = 'A user must be chosen.'
        else:
            # Find the user.
            user = User.query.filter(User.user_id == contact_form.user.data).first()
            # Create a new email message.
            message = Message(contact_form.subject.data, recipients=[user.get_email_address()])
            message.html = render_template(
                'email/message.html',
                user=user,
                subject=contact_form.subject.data,
                message=contact_form.message.data
            )
            # Send the message.
            mail.send(message)
            # Flash a success message.
            flash('Successfully sent message.')
            # Redirect to the dashboard.
            return redirect(url_for('tutor.dashboard'))

    return render_template(
        'tutor/contact.html', contact_form=contact_form, error=error
    )

@tutor_blueprint.route('/contactparent', methods=['GET', 'POST'])
@login_required(role="TUT")
def contact_parent():
    """
    Contact parent.
    """
    # Create an empty error.
    error = None

    # Create a form object.
    contact_form = ContactForm()

    # Select all the staff and tutors.
    contact_form.user.choices = [
        (parent.parent_id, parent.get_full_name()) for parent in select_parents()
    ]

    if request.method == 'POST' and contact_form.validate_on_submit():
        # Form is valid.
        # Check the staff members is not the default
        if contact_form.user.data == '0':
            error = 'A parent must be chosen.'
        else:
            # Find the user.
            parent = Parent.query.filter(Parent.parent_id == contact_form.user.data).first()
            # Create a new email message.
            message = Message(contact_form.subject.data, recipients=[parent.get_email_address()])
            message.html = render_template(
                'email/message.html',
                user=parent,
                subject=contact_form.subject.data,
                message=contact_form.message.data,
                parent=True
            )
            # Send the message.
            mail.send(message)
            # Flash a success message.
            flash('Successfully sent message.')
            # Redirect to the dashboard.
            return redirect(url_for('tutor.dashboard'))

    return render_template(
        'tutor/contactparent.html', contact_form=contact_form, error=error
    )

@tutor_blueprint.route('/personaldetails', methods=['GET', 'POST'])
@login_required(role="TUT")
def personal_details():
    """
    Edit personal details.
    """
    # Create the form object, for updating details.
    update_personal_details_form = UpdatePersonalDetailsForm()

    if request.method == 'POST' and update_personal_details_form.validate_on_submit():
        # Form is valid.
        # Ensure the update box is checked.
        if update_personal_details_form.update_details.data:
            # Update all the details.
            current_user.update_user_details(
                first_name=update_personal_details_form.tutor_first_name.data,
                last_name=update_personal_details_form.tutor_last_name.data,
                email_address=update_personal_details_form.tutor_email_address.data,
                telephone_number=update_personal_details_form.telephone_number.data,
                speciality=update_personal_details_form.speciality.data
            )
            # Save the changes.
            db.session.commit()
            # Flash a success method.
            flash('Successfully updated personal details.')
            # Redirect to this page - some weird stuff was
            # happening with get_personal_details
            return redirect(url_for('tutor.personal_details'))

    # Create a dictionary of the required personal details.
    user_details = current_user.get_personal_details()

    return render_template(
        'tutor/personaldetails.html',
        update_personal_details_form=update_personal_details_form,
        personal_details=user_details
    )

@tutor_blueprint.route('/timesheet', methods=['GET', 'POST'])
@login_required(role="TUT")
def timesheet():
    """
    Calculate the total amount of lesson time.
    """
    # Create new form objects for minimum and maximum dates.
    select_date_form = SelectMinMaxDateForm()
    # Set lessons and hours worked to None.
    time_sheet_lessons = hours_worked = None

    if request.method == 'POST' and select_date_form.validate_on_submit():
        # Set the min and max dates to the dates on the form.
        min_date = select_date_form.min_date.data
        max_date = select_date_form.max_date.data
    else:
        # This month.
        min_date = datetime.now()
        max_date = datetime.now() + timedelta(days=30)
        # Set the form defaults to these dates.
        select_date_form.min_date.default = min_date
        select_date_form.max_date.default = max_date
        # Process the form to update.
        select_date_form.process()

    # Select the lessons
    time_sheet_lessons = generate_timesheet(
        current_user, min_date, max_date
    )

    # Total the hours worked.
    hours_worked = total_time(time_sheet_lessons)

    # Return the template with the data.
    return render_template(
        'tutor/timesheet.html', time_sheet_lessons=time_sheet_lessons,
        hours_worked=hours_worked, select_date_form=select_date_form
    )
