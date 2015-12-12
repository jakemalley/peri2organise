# setup_admin.py
# Jake Malley
# Adds a new administrator to the database.

# Application Imports
from peri2organise import db
from peri2organise.models import User

# User Configuration Required:
FIRST_NAME = 'Admin'
LAST_NAME = 'Admin'
EMAIL_ADDRESS = 'admin@fromecollege.org'
PASSWORD = 'password1'
TELEPHONE_NUMBER = '01373465353'
SPECIALITY = 'Admin'
# -------------------------- #

# This script can only be run if there are no other admins!
if not User.query.filter(User.role == 'STA').all():
    # Create a new user object.
    admin_user = User()
    # Create a password hash of the desired password.
    password_hash = admin_user.create_password_hash(PASSWORD)
    # Update the admin user's details.
    admin_user.update_user_details(
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        email_address=EMAIL_ADDRESS,
        password=password_hash,
        role='STA',
        telephone_number=TELEPHONE_NUMBER,
        speciality=SPECIALITY
    )
    # Add the new object to the database.
    db.session.add(admin_user)
    # Commit changes.
    db.session.commit()
else:
    print("An admin already exists")
