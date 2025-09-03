import socket
from .base import *
from logging.config import dictConfig

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECURE_SETTINGS['django_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS['enable_debug']

# Because load balancer health checks will come from a different domain, 
# rather than restricting to specific domains or subdomains, we explicitly
# list the Application Load Balancer's (ALB) DNS name and the base domain. This allows
# for health checks from the load balancer and user agents/traffic to succeed
# while preventing host header attacks. This configuration is safe in
# our controlled ECS environment and avoids security issues of a wildcard setting.
ALLOWED_HOSTS = ['atg-dev-general-alb-1944621488.us-east-1.elb.amazonaws.com', '.tlt.harvard.edu']

# Add the container's own internal IP address for health checks
ALLOWED_HOSTS.append(socket.gethostbyname(socket.gethostname()))

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# AWS Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587  # Use 587 or 2587 to avoid timeouts when sending mail via Amazon SES
EMAIL_HOST_USER = SECURE_SETTINGS.get('email_host_user', '')
EMAIL_HOST_PASSWORD = SECURE_SETTINGS.get('email_host_password', '')

# Configure logging
dictConfig(LOGGING)
