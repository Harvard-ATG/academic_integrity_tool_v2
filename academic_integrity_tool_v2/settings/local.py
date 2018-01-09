from .base import *
from logging.config import dictConfig

DEBUG = True

SECRET_KEY = '1@7&11tb*l1c84uco-9=%(u#mb)_dl6%%++rihgnl&r)wmldrc'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS.extend(['debug_toolbar'])
MIDDLEWARE_CLASSES.extend(['debug_toolbar.middleware.DebugToolbarMiddleware'])

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Logging

# Log to console instead of a file when running locally
LOGGING['handlers']['default'] = {
    'level': logging.DEBUG,
    'class': 'logging.StreamHandler',
    'formatter': 'simple',
}

dictConfig(LOGGING)
