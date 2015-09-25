# utils.py
# Jake Malley
# Provides utilities to be used across the application.

# Imports
import os

def load_application_configuration(application):
    """
    Loads the configuration for the application,
    loads the configuration in the following order:
        1. Application defaults from peri2organise.config.DefaultConfiguration
        2. Settings file, peri2organise.conf located in the main 
           application folder (alongside manage.py).
        3. Additional settings can be read from a configuration file
           that is specified by an environment variable. 
           e.g. PERI2ORGANISE_CONFIG=/abs/path/to/peri2organise.conf
    """

    # Load DefaultConfiguration from peri2organise.config.DefaultConfiguration
    application.config.from_object('peri2organise.config.DefaultConfiguration')
    
    # Load configuration from file.
    CONFIGURATION_FILE = os.path.abspath('peri2organise.conf')
    try:
        application.config.from_pyfile(CONFIGURATION_FILE, silent=False)
    except IOError:
        # If the file doesn't exist, display the following error message.
        print(' * Could not load configuration %s.' %CONFIGURATION_FILE)
    except Exception as exception:
        # If an error occurred when processing the file, display the following message.
        print(' * Could not parse the configuration: %s.' %exception)

    # Load configuration from environment variable.
    try:
        application.config.from_envvar('PERI2ORGANISE_CONFIG')
    except RuntimeError as exception:
        print(' * Could not load the configuration from environment variable.\n%s.' %exception)
    except IOError as exception:
        print(' * Could not load the configuration from environment variable.\n%s.' %exception)
