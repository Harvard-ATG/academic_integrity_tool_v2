import requests
from .base import *
from logging.config import dictConfig

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECURE_SETTINGS['django_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS['enable_debug']

# Allow only the harvard.edu domain and subdomains, where the LTI tool itself is hosted
# i.e. academicintegritytoolv2.dev.tlt.harvard.edu
ALLOWED_HOSTS = ['.tlt.harvard.edu']

# -- Start dynamic IP retrieval
# The section below is for retrieving the instance's IP address when running on AWS EC2
# This allows for health checks to be performed against the instance itself.
# This is the standard header that AWS requires to access the metadata service.
AWS_METADATA_HEADER = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}

# This block attempts to get the instance's IP address.
try:
    # First, get the session token.
    token_url = "http://169.254.169.254/latest/api/token"
    token_response = requests.put(token_url, headers=AWS_METADATA_HEADER, timeout=2)
    token = token_response.text

    # Then, use the token to get the hostname.
    hostname_url = "http://169.254.169.254/latest/meta-data/local-ipv4"
    hostname_response = requests.get(hostname_url, headers={'X-aws-ec2-metadata-token': token}, timeout=2)
    instance_ip = hostname_response.text

    # If the IP is successfully retrieved, add it to the list.
    if instance_ip:
        ALLOWED_HOSTS.append(instance_ip)

    print(f"✅ Dynamically added instance IP {instance_ip} to ALLOWED_HOSTS.")

except requests.exceptions.RequestException as e:
    # This will be triggered if the code is not running on an EC2 instance.
    print("⚠️ Not running on EC2 or failed to get instance IP. Using default ALLOWED_HOSTS.")
    print(f"   Error: {e}")

# Make sure the list only contains unique values.
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

# Remove any empty host entries
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]
# --- End dynamic IP retrieval

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
