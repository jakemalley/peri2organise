# config.py
# Jake Malley
# Default Configuration Class

class DefaultConfiguration(object):
    """
    Default Configuration, to store all the default values required by the
    application, these values can be overridden by configuration options
    set within peri2organise.conf and PERI2ORGANISE_CONFIG environment variable.

    See peri2organise.utils.load_application_configuration for more details regarding
    configuration loading.
    """

    DEBUG = False