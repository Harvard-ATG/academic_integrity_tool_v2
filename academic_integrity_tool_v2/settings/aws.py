from .base import *
from logging.config import dictConfig

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECURE_SETTINGS['django_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS['enable_debug']

# Allow only the harvard.edu domain and subdomains, where the LTI tool itself is hosted
# i.e. academicintegritytoolv2.dev.tlt.harvard.edu
ALLOWED_HOSTS = ['.tlt.harvard.edu']

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True

# AWS Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587  # Use 587 or 2587 to avoid timeouts when sending mail via Amazon SES
EMAIL_HOST_USER = SECURE_SETTINGS.get('email_host_user', '')
EMAIL_HOST_PASSWORD = SECURE_SETTINGS.get('email_host_password', '')

# Configure logging
dictConfig(LOGGING)
