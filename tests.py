# tests.py
# Jake Malley
# Unit Tests for the application.

# Flask Imports
from flask.ext.testing import TestCase
from flask.ext.login import current_user
# Application Imports
from peri2organise import app
from peri2organise import db
from peri2organise.models import User
from peri2organise.models import Parent
from peri2organise.models import Lesson
from peri2organise.models import UserLessonAssociation
from peri2organise.models import Room
# Imports
import unittest
from datetime import datetime
from datetime import timedelta

class BaseTestCase(TestCase):
    """
    Base Test Case.
    """

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def default_HTTP_route_test(self, route, **kwargs):
        """
        Default route test, will test for a HTTP 200 response,
        ensure the error page / 400 error was not displayed.
        """
        response = self.client.get(route, content_type='html/text', follow_redirects=True)
        # Ensure we get a HTTP 200.
        self.assertEqual(response.status_code, 200)
        # Ensure we didn't get the 404 page.
        self.assertFalse('404' in response.data)
        # Ensure we were not redirected to the error page.
        self.assertFalse('Unfortunately the following error has occurred' in response.data)

        # See if we need to assert anything else.
        if 'assert_in_response' in kwargs:
            self.assertTrue(kwargs['assert_in_response'] in response.data)

class HomeBlueprintTests(BaseTestCase):
    """
    Tests all application routes, and ensures a HTTP 200
    was returned and not a 404.
    """

    # Test pages in the home blueprint.
    def test_site_index(self):
        """
        Test the site index.
        """
        self.default_HTTP_route_test('/')

    def test_terms_page(self):
        """
        Test the terms page.
        """
        self.default_HTTP_route_test('/terms')

class AuthBlueprintTests(BaseTestCase):
    """
    Tests all application routes, and ensures a HTTP 200
    was returned and not a 404.
    """

    def setUp(self):
        """
        Add a admin user to the database.
        """
        # Call the super class method.
        BaseTestCase.setUp(self)
        # Create a new user.
        staff_user = User()
        # Add Staff User
        staff_user.update_user_details(
            first_name="admin",
            last_name="admin",
            email_address="admin@test.com",
            password=staff_user.create_password_hash("password1"),
            role="STA",
        )
        db.session.add(staff_user)
        db.session.commit()

    # Test pages in the auth blueprint.
    def test_login_page(self):
        """
        Test the login page.
        """
        self.default_HTTP_route_test('/auth/login')

    def test_valid_login(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=dict(email_address="admin@test.com", password="password1"),
                follow_redirects=True
            )
            self.assertIn('Successfully Authenticated', response.data)
            self.assertTrue(current_user.first_name == "admin")
            self.assertTrue(current_user.is_active())

    def test_invalid_login(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=dict(email_address="admin@test.com", password="incorrect"),
                follow_redirects=True
            )
            self.assertIn('Invalid credentials', response.data)
            self.assertTrue(current_user.is_anonymous)
            self.assertFalse(current_user.is_active)

    def test_register_page(self):
        """
        Test the register page.
        """
        self.default_HTTP_route_test('/auth/register')

    def test_logout_page(self):
        """
        Test the logout page.
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data=dict(email_address="admin@test.com", password="password1"),
                follow_redirects=True
            )
            response = self.client.get('/auth/logout', follow_redirects=True)
            self.assertIn('Successfully logged out', response.data)
            self.assertFalse(current_user.is_active)

    def test_forgot_password_page(self):
        """
        Test the forgot_password page.
        """
        self.default_HTTP_route_test('/auth/forgotpassword')

    def test_reset_password_page(self):
        """
        Test the reset_password page.
        """
        self.default_HTTP_route_test('/auth/resetpassword')

class StudentBlueprintTest(BaseTestCase):
    """
    Tests all application routes, and ensures a HTTP 200
    was returned and not a 404.
    """

    def setUp(self):
        """
        Authenticate as a student before each request.
        """
        # Call the super class setup method.
        BaseTestCase.setUp(self)
        # Add a student, tutor and staff user to the database.
        staff_user = User()
        # Add Tutor User
        staff_user.update_user_details(
            first_name='staff',
            last_name='staff',
            email_address='staff@test.com',
            password=staff_user.create_password_hash('password1'),
            role='STA',
        )
        db.session.add(staff_user)
        tutor_user = User()
        # Add Tutor User
        tutor_user.update_user_details(
            first_name='tutor',
            last_name='tutor',
            email_address='tutor@test.com',
            password=tutor_user.create_password_hash('password1'),
            role='TUT',
        )
        db.session.add(tutor_user)
        student_user = User()
        # Add Student User 
        student_user.update_user_details(
            first_name='student',
            last_name='student',
            email_address='student@test.com',
            password=student_user.create_password_hash('password1'),
            role='STU',
        )
        db.session.add(student_user)

        # Add a new room.
        room = Room()
        room.update_room_details(
            location='Room1',
            facilities='Piano'
        )
        db.session.add(room)

        # Add a new lesson.
        lesson = Lesson()
        lesson.update_lesson_details(
            lesson_datetime=datetime.now() + timedelta(days=7),
            lesson_duration=3600,
            lesson_notes='Work Very Hard',
            room_id=1
        )
        lesson.users.append(tutor_user)
        lesson.users.append(student_user)
        db.session.add(lesson)

        # Commit the changes.
        db.session.commit()


        # Authenticate.
        with self.client:
            self.client.post(
                '/auth/login',
                data=dict(email_address='student@test.com', password='password1'),
                follow_redirects=True
            )

        # Set the IDs to use.
        self.STAFF_ID = staff_user.user_id
        self.TUTOR_ID = tutor_user.user_id
        self.STUDENT_ID = student_user.user_id

    def test_student_index(self):
        """
        Test the student index.
        """
        self.default_HTTP_route_test('/student/')

    def test_student_dashboard(self):
        """
        Test the student dashboard.
        """
        self.default_HTTP_route_test('/student/dashboard', assert_in_response='Student Dashboard')

    def test_lessons(self):
        """
        Test the lessons page.
        """
        self.default_HTTP_route_test('/student/lessons', assert_in_response='Lessons')
        self.default_HTTP_route_test('/student/lessons', assert_in_response='Work Very Hard')

    def test_view_lesson(self):
        """
        Test the view lesson page.
        """
        self.default_HTTP_route_test('/student/lessons/1', assert_in_response='View Lesson')
        self.default_HTTP_route_test('/student/lessons/1', assert_in_response='Work Very Hard')

    def test_tutors(self):
        """
        Test the tutors page.
        """
        self.default_HTTP_route_test('/student/tutors', assert_in_response='Peripatetic Tutors')
        self.default_HTTP_route_test('/student/tutors', assert_in_response='Tutor Tutor')

    def test_view_tutor(self):
        """
        Test the tutors page.
        """
        self.default_HTTP_route_test('/student/tutors/'+str(self.TUTOR_ID), assert_in_response='View Tutor')
        self.default_HTTP_route_test('/student/tutors/'+str(self.TUTOR_ID), assert_in_response='Tutor Tutor')

    def test_staff(self):
        """
        Test the staff page.
        """
        self.default_HTTP_route_test('/student/staff', assert_in_response='Staff Members')
        self.default_HTTP_route_test('/student/staff', assert_in_response='Staff Staff')

    def test_view_staff(self):
        """
        Test the staff page.
        """
        self.default_HTTP_route_test('/student/staff/'+str(self.STAFF_ID), assert_in_response='View Staff Member')
        self.default_HTTP_route_test('/student/staff/'+str(self.STAFF_ID), assert_in_response='Staff Staff')

    def test_attendance(self):
        """
        Test the attendance page.
        """
        self.default_HTTP_route_test('/student/attendance', assert_in_response='Attendance')

    def test_personal_details(self):
        """
        Test the personal details page.
        """
        self.default_HTTP_route_test('/student/personaldetails', assert_in_response='Personal Details')
        self.default_HTTP_route_test('/student/personaldetails', assert_in_response='student@test.com')

    def test_contact(self):
        """
        Test the contact page.
        """
        self.default_HTTP_route_test('/student/contact', assert_in_response='Contact Staff Member')

class TutorBlueprintTest(BaseTestCase):
    """
    Tests all application routes, and ensures a HTTP 200
    was returned and not a 404.
    """

    def setUp(self):
        """
        Authenticate as a tutor before each request.
        """
        # Call the super class setup method.
        BaseTestCase.setUp(self)
        # Add a student, tutor, parent and staff user to the database.
        staff_user = User()
        # Add Tutor User
        staff_user.update_user_details(
            first_name='staff',
            last_name='staff',
            email_address='staff@test.com',
            password=staff_user.create_password_hash('password1'),
            role='STA',
        )
        db.session.add(staff_user)
        tutor_user = User()
        # Add Tutor User
        tutor_user.update_user_details(
            first_name='tutor',
            last_name='tutor',
            email_address='tutor@test.com',
            password=tutor_user.create_password_hash('password1'),
            role='TUT',
        )
        db.session.add(tutor_user)
        # Add a parent.
        parent = Parent()
        parent.update_parent_details(
            first_name='parent',
            last_name='parent',
            email_address='parent@test.com',
            telephone_number='01234567890'
        )
        db.session.add(parent)
        student_user = User()
        # Add Student User 
        student_user.update_user_details(
            first_name='student',
            last_name='student',
            email_address='student@test.com',
            password=student_user.create_password_hash('password1'),
            role='STU',
            tutor_group='ABC',
            musical_instrument_type='Instrument',
            musical_instrument='Piano',
            musical_style='jazz',
            lesson_type='individual',
            parent_id=1,
        )
        db.session.add(student_user)

        # Add a new room.
        room = Room()
        room.update_room_details(
            location='Room1',
            facilities='Piano'
        )
        db.session.add(room)

        # Add a new lesson.
        lesson = Lesson()
        lesson.update_lesson_details(
            lesson_datetime=datetime.now() + timedelta(days=7),
            lesson_duration=3600,
            lesson_notes='Work Very Hard',
            room_id=1
        )
        lesson.users.append(tutor_user)
        lesson.users.append(student_user)
        db.session.add(lesson)

        # Commit the changes.
        db.session.commit()


        # Authenticate.
        with self.client:
            self.client.post(
                '/auth/login',
                data=dict(email_address='tutor@test.com', password='password1'),
                follow_redirects=True
            )

        # Set the IDs to use.
        self.STAFF_ID = staff_user.user_id
        self.TUTOR_ID = tutor_user.user_id
        self.STUDENT_ID = student_user.user_id
        self.PARENT_ID = parent.parent_id

    def test_tutor_index(self):
        """
        Test the tutor index.
        """
        self.default_HTTP_route_test('/tutor/')

    def test_tutor_dashboard(self):
        """
        Test the tutor dashboard.
        """
        self.default_HTTP_route_test('/tutor/dashboard', assert_in_response='Tutor Dashboard')

    def test_lessons(self):
        """
        Test the lessons page.
        """
        self.default_HTTP_route_test('/tutor/lessons', assert_in_response='Lessons')
        self.default_HTTP_route_test('/tutor/lessons', assert_in_response='Work Very Hard')

    def test_view_lesson(self):
        """
        Test the view lesson page.
        """
        self.default_HTTP_route_test('/tutor/lessons/1', assert_in_response='View Lesson')
        self.default_HTTP_route_test('/tutor/lessons/1', assert_in_response='Work Very Hard')

    def test_add_lesson(self):
        """
        Test the add lesson page.
        """
        self.default_HTTP_route_test('/tutor/lessons/add', assert_in_response='Add Lesson')

    def test_edit_lesson(self):
        """
        Test the edit lesson page.
        """
        self.default_HTTP_route_test('/tutor/lessons/edit/1', assert_in_response='Edit Lesson')

    def test_students(self):
        """
        Test the students page.
        """
        self.default_HTTP_route_test('/tutor/students', assert_in_response='Students')

    def test_view_student(self):
        """
        Test the view student page.
        """
        self.default_HTTP_route_test('/tutor/students/'+str(self.STUDENT_ID), assert_in_response='View Student')

    def test_view_parent(self):
        """
        Test the view parent page.
        """
        self.default_HTTP_route_test('/tutor/parents/'+str(self.PARENT_ID), assert_in_response='View Parent')
        self.default_HTTP_route_test('/tutor/parents/'+str(self.PARENT_ID), assert_in_response='parent@test.com')

    def test_attendance(self):
        """
        Test the attendance page.
        """
        self.default_HTTP_route_test('/tutor/attendance', assert_in_response='Attendance')

    def test_record_attendance(self):
        """
        Test the record attendance page.
        """
        self.default_HTTP_route_test('/tutor/attendance/record/1', assert_in_response='Record Attendance')
        self.default_HTTP_route_test('/tutor/attendance/record/1', assert_in_response='The register has not been fully taken for this lesson yet. Ensure all students have recorded attendance.')

    def test_view_attendance(self):
        """
        Test the view attendance page.
        """
        self.default_HTTP_route_test('/tutor/attendance/view/1', assert_in_response='View Attendance')
        self.default_HTTP_route_test('/tutor/attendance/view/1', assert_in_response='Work Very Hard')
        self.default_HTTP_route_test('/tutor/attendance/view/1', assert_in_response='Student Student')

    def test_contact(self):
        """
        Test the contact page.
        """
        self.default_HTTP_route_test('/tutor/contact', assert_in_response='Contact User')

    def test_contact_parent(self):
        """
        Test the contact parent page.
        """
        self.default_HTTP_route_test('/tutor/contactparent', assert_in_response='Contact Parent')

    def test_personal_details(self):
        """
        Test the personal details page.
        """
        self.default_HTTP_route_test('/tutor/personaldetails', assert_in_response='Personal Details')
        self.default_HTTP_route_test('/tutor/personaldetails', assert_in_response='tutor@test.com')

    def test_timesheet(self):
        """
        Test the timesheet page.
        """
        self.default_HTTP_route_test('/tutor/personaldetails', assert_in_response='Time Sheet')

class StaffBlueprintTest(BaseTestCase):
    """
    Tests all application routes, and ensures a HTTP 200
    was returned and not a 404.
    """

    def setUp(self):
        """
        Authenticate as staff before each request.
        """
        # Call the super class setup method.
        BaseTestCase.setUp(self)
        # Add a student, tutor, parent and staff user to the database.
        staff_user = User()
        # Add Tutor User
        staff_user.update_user_details(
            first_name='staff',
            last_name='staff',
            email_address='staff@test.com',
            password=staff_user.create_password_hash('password1'),
            role='STA',
        )
        db.session.add(staff_user)
        tutor_user = User()
        # Add Tutor User
        tutor_user.update_user_details(
            first_name='tutor',
            last_name='tutor',
            email_address='tutor@test.com',
            password=tutor_user.create_password_hash('password1'),
            role='TUT',
        )
        db.session.add(tutor_user)
        # Add a parent.
        parent = Parent()
        parent.update_parent_details(
            first_name='parent',
            last_name='parent',
            email_address='parent@test.com',
            telephone_number='01234567890'
        )
        db.session.add(parent)
        student_user = User()
        # Add Student User 
        student_user.update_user_details(
            first_name='student',
            last_name='student',
            email_address='student@test.com',
            password=student_user.create_password_hash('password1'),
            role='STU',
            tutor_group='ABC',
            musical_instrument_type='Instrument',
            musical_instrument='Piano',
            musical_style='jazz',
            lesson_type='individual',
            parent_id=1,
        )
        db.session.add(student_user)

        # Add a new room.
        room = Room()
        room.update_room_details(
            location='Room1',
            facilities='Piano'
        )
        db.session.add(room)

        # Add a new lesson.
        lesson = Lesson()
        lesson.update_lesson_details(
            lesson_datetime=datetime.now() + timedelta(days=7),
            lesson_duration=3600,
            lesson_notes='Work Very Hard',
            room_id=1
        )
        lesson.users.append(tutor_user)
        lesson.users.append(student_user)
        db.session.add(lesson)

        # Commit the changes.
        db.session.commit()


        # Authenticate.
        with self.client:
            self.client.post(
                '/auth/login',
                data=dict(email_address='staff@test.com', password='password1'),
                follow_redirects=True
            )

        # Set the IDs to use.
        self.STAFF_ID = staff_user.user_id
        self.TUTOR_ID = tutor_user.user_id
        self.STUDENT_ID = student_user.user_id
        self.PARENT_ID = parent.parent_id

    def test_staff_index(self):
        """
        Test the staff index.
        """
        self.default_HTTP_route_test('/staff/')

    def test_staff_dashboard(self):
        """
        Test the staff dashboard.
        """
        self.default_HTTP_route_test('/staff/dashboard', assert_in_response='Tutor Dashboard')

    def test_lessons(self):
        """
        Test the lessons page.
        """
        self.default_HTTP_route_test('/staff/lessons', assert_in_response='Lessons')
        self.default_HTTP_route_test('/staff/lessons', assert_in_response='Work Very Hard')

    def test_view_lesson(self):
        """
        Test the view lesson page.
        """
        self.default_HTTP_route_test('/staff/lessons/1', assert_in_response='View Lesson')
        self.default_HTTP_route_test('/staff/lessons/1', assert_in_response='Work Very Hard')

    def test_add_lesson(self):
        """
        Test the add lesson page.
        """
        self.default_HTTP_route_test('/staff/lessons/add', assert_in_response='Add Lesson')

    def test_edit_lesson(self):
        """
        Test the edit lesson page.
        """
        self.default_HTTP_route_test('/staff/lessons/edit/1', assert_in_response='Edit Lesson')

    def test_students(self):
        """
        Test the students page.
        """
        self.default_HTTP_route_test('/staff/students', assert_in_response='Students')

    def test_view_student(self):
        """
        Test the view student page.
        """
        self.default_HTTP_route_test('/staff/students/'+str(self.STUDENT_ID), assert_in_response='View Student')

    def test_parents(self):
        """
        Test the parents page.
        """
        self.default_HTTP_route_test('/staff/parents', assert_in_response='Parents')

    def test_view_parent(self):
        """
        Test the view parent page.
        """
        self.default_HTTP_route_test('/staff/parents/'+str(self.PARENT_ID), assert_in_response='View Parent')
        self.default_HTTP_route_test('/staff/parents/'+str(self.PARENT_ID), assert_in_response='parent@test.com')

    def test_tutors(self):
        """
        Test the tutors page.
        """
        self.default_HTTP_route_test('/staff/tutors', assert_in_response='Tutors')
        self.default_HTTP_route_test('/staff/tutors', assert_in_response='tutor@test.com')

    def test_view_tutor(self):
        """
        Test the view tutor page.
        """
        self.default_HTTP_route_test('/staff/tutors/'+str(self.TUTOR_ID), assert_in_response='View Tutor')
        self.default_HTTP_route_test('/staff/tutors/'+str(self.TUTOR_ID), assert_in_response='tutor@test.com')

    def test_staff(self):
        """
        Test the staffs page.
        """
        self.default_HTTP_route_test('/staff/staff', assert_in_response='Staff Members')
        self.default_HTTP_route_test('/staff/staff', assert_in_response='staff@test.com')

    def test_view_staff(self):
        """
        Test the view staff page.
        """
        self.default_HTTP_route_test('/staff/staff/'+str(self.STAFF_ID), assert_in_response='View Staff Member')
        self.default_HTTP_route_test('/staff/staff/'+str(self.STAFF_ID), assert_in_response='staff@test.com')

    def test_attendance(self):
        """
        Test the attendance page.
        """
        self.default_HTTP_route_test('/staff/attendance', assert_in_response='Attendance')

    def test_record_attendance(self):
        """
        Test the record attendance page.
        """
        self.default_HTTP_route_test('/staff/attendance/record/1', assert_in_response='Record Attendance')
        self.default_HTTP_route_test('/staff/attendance/record/1', assert_in_response='The register has not been fully taken for this lesson yet. Ensure all students have recorded attendance.')

    def test_view_attendance(self):
        """
        Test the view attendance page.
        """
        self.default_HTTP_route_test('/staff/attendance/view/1', assert_in_response='View Attendance')
        self.default_HTTP_route_test('/staff/attendance/view/1', assert_in_response='Work Very Hard')
        self.default_HTTP_route_test('/staff/attendance/view/1', assert_in_response='Student Student')

    def test_contact(self):
        """
        Test the contact page.
        """
        self.default_HTTP_route_test('/staff/contact', assert_in_response='Contact User')

    def test_contact_parent(self):
        """
        Test the contact parent page.
        """
        self.default_HTTP_route_test('/staff/contactparent', assert_in_response='Contact Parent')

    def test_personal_details(self):
        """
        Test the personal details page.
        """
        self.default_HTTP_route_test('/staff/personaldetails', assert_in_response='Personal Details')
        self.default_HTTP_route_test('/staff/personaldetails', assert_in_response='staff@test.com')

    def test_add_user(self):
        """
        Test the add user page.
        """
        self.default_HTTP_route_test('/staff/users/add', assert_in_response='Add User')

    def test_access_tutor_dashboard(self):
        """
        Test the staff user's access to the tutor dashboard.
        """
        self.default_HTTP_route_test('/tutor/dashboard', assert_in_response='Tutor Dashboard')

if __name__ == '__main__':
    # Test the application.
    unittest.main()