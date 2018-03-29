# For running unit tests
from .base import *
from logging.config import dictConfig

DEBUG = True

SECRET_KEY = 'testing'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    },
}

LOGGING['handlers']['default'] = {
    'level': logging.DEBUG,
    'class': 'logging.StreamHandler',
    'formatter': 'simple',
}

dictConfig(LOGGING)