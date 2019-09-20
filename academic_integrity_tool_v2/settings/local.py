from .base import *
from logging.config import dictConfig

DEBUG = True
DEBUG_TOOLBAR = False

SECRET_KEY = '1@7&11tb*l1c84uco-9=%(u#mb)_dl6%%++rihgnl&r)wmldrc'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


if DEBUG_TOOLBAR:
    INSTALLED_APPS.extend(['debug_toolbar'])
    MIDDLEWARE.extend(['debug_toolbar.middleware.DebugToolbarMiddleware'])
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)


# Logging

# Log to console instead of a file when running locally
LOGGING['handlers']['default'] = {
    'level': logging.DEBUG,
    'class': 'logging.StreamHandler',
    'formatter': 'simple',
}

dictConfig(LOGGING)
