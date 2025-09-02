from .base import *
from logging.config import dictConfig
import os

DEBUG = True

SECRET_KEY = '1@7&11tb*l1c84uco-9=%(u#mb)_dl6%%++rihgnl&r)wmldrc'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ngrok-free.app']

try:
    ngrok_domain = os.environ['NGROK_DOMAIN']
    ALLOWED_HOSTS.append(ngrok_domain)
except KeyError:
    # Key Error indicates that there is no NGROK_DOMAIN to add, so just continue
    pass

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
