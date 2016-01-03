# views.py
# Jake Malley
# Views used in the staff blueprint.

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
from peri2organise.student.utils import select_user
from peri2organise.student.utils import select_users_by_roles
from peri2organise.student.forms import ContactForm
from peri2organise.tutor.forms import AddLessonForm
from peri2organise.tutor.forms import EditLessonForm
from peri2organise.tutor.forms import SelectMinMaxDateForm
from peri2organise.tutor.forms import RecordSingleAttendanceForm
from peri2organise.tutor.forms import UpdatePersonalDetailsForm
from peri2organise.tutor.utils import select_parents
from peri2organise.tutor.utils import check_attendance_complete
from peri2organise.tutor.utils import send_lesson_update
from peri2organise.staff.forms import FilterLessonsForm
from peri2organise.staff.forms import AddUserForm
# Imports
from datetime import datetime
from datetime import time
from datetime import timedelta

# Create tutor blueprint.
staff_blueprint = Blueprint('staff',__name__)

@staff_blueprint.route('/')
@login_required(roles=['STA'])
def index():
    """
    Index, redirect to dashboard.
    """
    return redirect(url_for('staff.dashboard'))

@staff_blueprint.route('/dashboard')
@login_required(roles=['STA'])
def dashboard():
    """
    Staff dashboard.
    """
    # Select all of the days lessons.
    todays_lessons = Lesson.query.filter(
        Lesson.lesson_datetime >= datetime.now().date()
    ).filter(
        Lesson.lesson_datetime <= datetime.now().date() + timedelta(days=1)
    ).order_by(
        Lesson.lesson_datetime.asc()
    ).all()

    return render_template('staff/dashboard.html', todays_lessons=todays_lessons)

@staff_blueprint.route('/lessons', methods=['GET', 'POST'])
@login_required(roles=['STA'])
def lessons():
    """
    View all lessons.
    """
    # Create filter lessons form object.
    filter_lessons_form = FilterLessonsForm()

    # If the method was post and the form was valid.
    if request.method == 'POST' and filter_lessons_form.validate_on_submit():
        if filter_lessons_form.include_future_lessons.data and \
            filter_lessons_form.include_past_lessons.data:
            all_lessons = Lesson.query.order_by(Lesson.lesson_datetime.asc()).all()
        elif filter_lessons_form.include_future_lessons.data:
            all_lessons = Lesson.query.filter(
                Lesson.lesson_datetime >= datetime.now()
            ).order_by(Lesson.lesson_datetime.asc()).all()
        elif filter_lessons_form.include_past_lessons.data:
            all_lessons = Lesson.query.filter(
                Lesson.lesson_datetime <= datetime.now()
            ).order_by(Lesson.lesson_datetime.asc()).all()
        else:
            all_lessons = []
    else:
        # Only select future.
        all_lessons = Lesson.query.filter(
            Lesson.lesson_datetime >= datetime.now()
        ).order_by(Lesson.lesson_datetime.asc()).all()

    return render_template(
        'staff/lessons.html', all_lessons=all_lessons, filter_lessons_form=filter_lessons_form
    )

@staff_blueprint.route('/lessons/<int:lesson_id>')
@login_required(roles=['STA'])
def view_lesson(lesson_id):
    """
    View a single lesson.
    """
    # Get the UserLessonAssociation with the
    # the given lesson id. (So we can also display attendance etc.)
    assoc = UserLessonAssociation.query.filter(UserLessonAssociation.lesson_id == lesson_id).first()

    # Ensure the lesson id/association object is found.
    if not assoc:
        abort(404)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'staff/view_lesson.html', lesson=assoc.lesson, assoc=assoc
    )

@staff_blueprint.route('/lessons/add', methods=['GET', 'POST'])
@login_required(roles=['STA'])
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

            # Send an update.
            if app.config['UPDATE_ON_NEW_LESSON']:
                # Send an email update.
                html = 'A new lesson has been created on: ' + new_lesson.get_lesson_date()

                # Send a lesson update.
                send_lesson_update(
                    user_object, html,
                    url_for('student.lessons', _external=True)
                )

        # Flash a success message.
        flash("Successfully added new lesson.")

        # Add the lesson to the db.
        db.session.add(new_lesson)
        # Commit changes.
        db.session.commit()

        return redirect(url_for('staff.add_lesson'))

    return render_template(
        'staff/add_lesson.html', add_lesson_form=add_lesson_form, error=error
    )

@staff_blueprint.route('/lessons/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required(roles=['STA'])
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

    # Find the lesson with the given ID.
    lesson = Lesson.query.filter(Lesson.lesson_id == lesson_id).first()

    # All the users that can be removed are the users of the lesson.
    edit_lesson_form.remove_users.choices = [
        (user.user_id, user.get_full_name()) for user in lesson.users
    ]

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

        if app.config['UPDATE_ON_EDIT_LESSON']:
            # Iterate through the users and send updates.
            for user in lesson.users:
                if user.get_role() == 'STU':
                    # Send an email update.
                    html = 'Your lesson on: ' + lesson.get_lesson_date() + \
                        ' has been updated.'

                    # Send a lesson update.
                    send_lesson_update(
                        user, html,
                        url_for(
                            'student.view_lesson',
                            lesson_id=lesson.lesson_id,
                            _external=True
                        )
                    )

        # Iterate through the users to add.
        for user_id in edit_lesson_form.add_users.data:
            # Select the user object.
            user_object = select_user(user_id)
            # If the user is not already going to the lesson.
            if user_object not in lesson.users:
                # Append it to the lessons users.
                lesson.users.append(user_object)

                # Send an email update.
                html = 'You have been added to a lesson on: ' + lesson.get_lesson_date()

                # Send a lesson update.
                send_lesson_update(
                    user_object, html,
                    url_for(
                        'student.view_lesson',
                        lesson_id=lesson.lesson_id,
                        _external=True
                    )
                )
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
            # Send an email update.
            html = 'You have been removed from the lesson on: ' + lesson.get_lesson_date() \
                + ' this means your attendance is no longer required.'

            # Send a lesson update.
            send_lesson_update(
                User.query.filter(User.user_id == user_id).first(), html,
                url_for('student.lessons', _external=True)
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
        'staff/edit_lesson.html', edit_lesson_form=edit_lesson_form, lesson=lesson
    )

@staff_blueprint.route('/students')
@login_required(roles=['STA'])
def students():
    """
    View all students.
    """
    # Select the students.
    all_students = User.query.filter(User.role == 'STU').order_by(User.last_name).all()
    # Render the students template.
    return render_template(
        'staff/students.html', students=all_students
    )

@staff_blueprint.route('/students/<int:student_id>')
@login_required(roles=['STA'])
def view_student(student_id):
    """
    View a single student.
    """
    # Find the student.
    student = select_user(student_id, role='STU')
    # Check the user exists.
    if student is not None:
        return render_template(
            'staff/view_student.html', student=student
        )
    else:
        # If the student isn't found, return a 404.
        abort(404)

@staff_blueprint.route('/parents')
@login_required(roles=['STA'])
def parents():
    """
    View all parents.
    """
    # Select all parents.
    all_parents = Parent.query.order_by(Parent.last_name).all()
    # Render the parents template.
    return render_template(
        'staff/parents.html', parents=all_parents
    )

@staff_blueprint.route('/parents/<int:parent_id>')
@login_required(roles=['STA'])
def view_parent(parent_id):
    """
    View a single parent.
    """
    # Select the parent.
    parent = select_parents(parent_id=parent_id, single=True)
    # Check the parent exists.
    if parent is not None:
        return render_template(
            'staff/view_parent.html', parent=parent
        )
    else:
        # If the parent isn't found, return a 404.
        abort(404)

@staff_blueprint.route('/tutors')
@login_required(roles=['STA'])
def tutors():
    """
    View all tutors.
    """
    # Select all tutors.
    all_tutors = User.query.filter(User.role == 'TUT').order_by(User.last_name).all()
    # Render the tutors template.
    return render_template(
        'staff/tutors.html', tutors=all_tutors
    )

@staff_blueprint.route('/tutors/<int:tutor_id>')
@login_required(roles=['STA'])
def view_tutor(tutor_id):
    """
    View a single tutor.
    """
    # Find the tutor.
    tutor = select_user(tutor_id, role='TUT')
    # Check the user exists.
    if tutor is not None:
        return render_template(
            'staff/view_tutor.html', tutor=tutor
        )
    else:
        # If the tutor isn't found, return a 404.
        abort(404)

@staff_blueprint.route('/staff')
@login_required(roles=['STA'])
def staff():
    """
    View all staff.
    """
    # Select all staff.
    all_staff = User.query.filter(User.role == 'STA').order_by(User.last_name).all()
    # Render the staff template.
    return render_template(
        'staff/staff.html', staff=all_staff
    )

@staff_blueprint.route('/staff/<int:staff_id>')
@login_required(roles=['STA'])
def view_staff(staff_id):
    """
    View a single staff member.
    """
    # Find the staff member.
    staff_member = select_user(staff_id, role='STA')
    # Check the user exists.
    if staff_member is not None:
        return render_template(
            'staff/view_staff.html', staff_member=staff_member
        )
    else:
        # If the staff_member isn't found, return a 404.
        abort(404)

@staff_blueprint.route('/attendance', methods=['GET', 'POST'])
@login_required(roles=['STA'])
def attendance():
    """
    Display all lessons attendance can be recorded for.
    """
    # Create new form objects for minimum and maximum dates.
    select_date_form = SelectMinMaxDateForm()

    if request.method == 'POST' and select_date_form.validate_on_submit():
        # Form was submitted and is valid, filter by dates.
        no_attendance_recorded = Lesson.query.filter(Lesson.attendance_recorded == False).filter(
            Lesson.lesson_datetime >= select_date_form.min_date.data
        ).filter(
            Lesson.lesson_datetime <= select_date_form.max_date.data + timedelta(days=1)
        ).all()

    else:
        # Select all lessons with recorded attendance.
        no_attendance_recorded = Lesson.query.filter(Lesson.attendance_recorded == False).all()

    # Render the attendance template.
    return render_template(
        'staff/attendance.html',
        no_attendance_recorded=no_attendance_recorded,
        select_date_form=select_date_form
    )

@staff_blueprint.route('/attendance/record/<int:lesson_id>', methods=['GET', 'POST'])
@login_required(roles=['STA'])
def record_attendance(lesson_id):
    """
    Record attendance for a lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    lesson = Lesson.query.filter(Lesson.lesson_id == lesson_id).first()

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

        # We only want to send updates if they we're late or not there.
        if assoc.attendance_code == 'L' or assoc.attendance_code == 'N':
            # Send an email update.
            html = 'Attendance for your lesson on: ' + assoc.lesson.get_lesson_date() \
                + ' has been updated. Your attendance is now recorded as: ' + \
                assoc.get_lesson_attendance_str()

            # Send a lesson update.
            send_lesson_update(
                assoc.user, html,
                url_for(
                    'student.view_lesson',
                    lesson_id=lesson_id,
                    _external=True
                ),
                parent=True
            )

        if check_attendance_complete(lesson):
            # The attendance is complete.
            lesson.update_lesson_details(attendance_recorded=True)
        else:
            lesson.update_lesson_details(attendance_recorded=False)

        # Save Changes
        db.session.commit()

        # Refresh
        return redirect(url_for('staff.record_attendance', lesson_id=lesson_id))

    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'staff/record_attendance.html', lesson=lesson,
        record_single_attendance_form=record_single_attendance_form
    )

@staff_blueprint.route('/attendance/view/<int:lesson_id>')
@login_required(roles=['STA'])
def view_attendance(lesson_id):
    """
    View attendance for a lesson.
    """
    # Get the UserLessonAssociation for the current and
    # the given lesson id. (So we can also display attendance etc.)
    lesson = Lesson.query.filter(Lesson.lesson_id == lesson_id).first()

    # Ensure the lesson id/association object is found.
    if not lesson:
        abort(404)
    # Render the view lesson template and pass in the association and the lesson object.
    return render_template(
        'staff/view_attendance.html', lesson=lesson,
    )

@staff_blueprint.route('/contact', methods=['GET', 'POST'])
@login_required(roles=['STA'])
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
            return redirect(url_for('staff.dashboard'))

    return render_template(
        'staff/contact.html', contact_form=contact_form, error=error
    )

@staff_blueprint.route('/contactparent', methods=['GET', 'POST'])
@login_required(roles=['STA'])
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
            return redirect(url_for('staff.dashboard'))

    return render_template(
        'tutor/contactparent.html', contact_form=contact_form, error=error
    )

@staff_blueprint.route('/personaldetails', methods=['GET', 'POST'])
@login_required(roles=['STA'])
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
            return redirect(url_for('staff.personal_details'))

    # Create a dictionary of the required personal details.
    user_details = current_user.get_personal_details()

    return render_template(
        'staff/personaldetails.html',
        update_personal_details_form=update_personal_details_form,
        personal_details=user_details
    )

@staff_blueprint.route('/users/add', methods=['GET', 'POST'])
@login_required(roles=['STA'])
def add_user():
    """
    Add a new user to the database.
    """
    # Empty error variable.
    error = None
    # Create the form object.
    add_user_form = AddUserForm()

    # Check to see if the method was post and the form was valid.
    if request.method == 'POST' and add_user_form.validate_on_submit() \
        and add_user_form.validate_optional_form_fields():
        # Create new user object.
        new_user = User()
        # Create password hash
        password_hash = new_user.create_password_hash(add_user_form.password.data)
        # Update generic details.
        new_user.update_user_details(
            first_name=add_user_form.first_name.data,
            last_name=add_user_form.last_name.data,
            email_address=add_user_form.email_address.data,
            role=add_user_form.role.data,
            password=password_hash
        )
        # Check to see if the user is a student or a tutor/staff.
        if add_user_form.role.data == 'STU':
            # Check there isn't already a parent with these details.
            parent = Parent.query.filter_by(
                email_address=add_user_form.parent_email_address.data
            ).first()
            # If the parent exists.
            if parent is not None:
                # Parent already exists, lets use there details.
                # But check the phone number also matches.
                if parent.get_telephone_number() != add_user_form.parent_telephone_number.data:
                    error = "A parent is already associated with this email address, \
                        but could not be added to this student as the telephone number \
                        provided did not match. Please either use a different email address \
                        or the same telephone number as previously used."

                    return render_template(
                        'staff/add_user.html',
                        add_user_form=add_user_form,
                        error=error
                    )

                else:
                    # If the telephone number matched, use this parent's ID.
                    parent_id = parent.parent_id
            else:
                # Add new parent.
                new_parent = Parent()
                # Update the new parent's details.
                new_parent.update_parent_details(
                    first_name=add_user_form.parent_first_name.data,
                    last_name=add_user_form.parent_last_name.data,
                    email_address=add_user_form.parent_email_address.data,
                    telephone_number=add_user_form.parent_telephone_number.data
                )
                # Add the new parent to the database.
                db.session.add(new_parent)
                # Commit the changes to the database.
                db.session.commit()
                # Get the parent_id.
                parent_id = new_parent.parent_id

            if add_user_form.musical_instrument.data == 'singing':
                new_user_musical_instrument = 'Voice'
            else:
                new_user_musical_instrument = add_user_form.musical_instrument.data

            # Update student specific details.
            new_user.update_user_details(
                tutor_group=add_user_form.tutor_group.data,
                musical_instrument_type=add_user_form.musical_instrument_type.data,
                musical_instrument=new_user_musical_instrument,
                musical_style=add_user_form.musical_style.data,
                musical_grade=int(add_user_form.musical_grade.data),
                lesson_type=add_user_form.lesson_type.data,
                lesson_pairing=add_user_form.lesson_pairing.data,
                parent_id=parent_id
            )
        elif add_user_form.role.data == 'TUT' or add_user_form.role.data == 'STA':
            # Update staff/tutor specific details.
            new_user.update_user_details(
                speciality=add_user_form.speciality.data,
                telephone_number=add_user_form.telephone_number.data
            )

        # Add the new user.
        db.session.add(new_user)
        # Commit the changes.
        db.session.commit()
        # Success message.
        flash("Successfully added new user.")

        # Redirect.
        return redirect(url_for('staff.add_user'))

    return render_template(
        'staff/add_user.html',
        add_user_form=add_user_form,
        error=error
    )
