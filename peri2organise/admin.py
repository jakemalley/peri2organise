# admin.py
# Jake Malley
# File for configuration of flask-admin.

# Flask Imports
from flask import redirect
from flask import request
from flask import url_for
from flask.ext.admin import Admin
from flask.ext.admin import AdminIndexView
from flask.ext.admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext.login import current_user
# Application Import
from peri2organise import app
from peri2organise import db
from peri2organise.auth.utils import unauthorized_role
from peri2organise.models import User
from peri2organise.models import Parent
from peri2organise.models import Lesson
from peri2organise.models import Instrument
from peri2organise.models import Room
from peri2organise.models import UserLessonAssociation

class AuthenticationMixin(object):

    def is_accessible(self):
        """
        If the user is authenticated and they are staff they
        should be able to access the page.
        """
        return current_user.is_authenticated and current_user.get_role() == 'STA'

    def _handle_view(self, name, **kwargs):
        # If not able to login.
        if not self.is_accessible():
            if current_user.is_authenticated:
                # Return unauthorized role error.
                return unauthorized_role()
            else:
                # Redirect to login page.
                return redirect(url_for('auth.login', next=request.url))

class AdminIndex(AuthenticationMixin, AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class SecureModelView(AuthenticationMixin, ModelView):

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class UserAdmin(SecureModelView):

    """
    Custom View for the user model.
    """

    # Exclude password.
    column_exclude_list = [
        'password', 'tutor_group', 'musical_instrument_type', 'musical_instrument',
        'musical_style', 'musical_grade', 'lesson_type', 'lesson_pairing', 'parent',
        'speciality'
    ]

# Create flask-admin object.
admin = Admin(app, name='peri2organise', template_mode='bootstrap3', index_view=AdminIndex(url='/admin'))
# Add views for all the models.
admin.add_view(UserAdmin(User, db.session))
admin.add_view(SecureModelView(Parent, db.session))
admin.add_view(SecureModelView(Lesson, db.session))
admin.add_view(SecureModelView(Instrument, db.session))
admin.add_view(SecureModelView(Room, db.session))
admin.add_view(SecureModelView(UserLessonAssociation, db.session))