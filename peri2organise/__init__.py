# __init__.py
# Jake Malley
# Initialize application.

# Flask Imports
from flask import Flask
# Application Imports
from peri2organise.utils import load_application_configuration

# Create application object.
app = Flask(__name__)
# Load the configuration.
load_application_configuration(app)