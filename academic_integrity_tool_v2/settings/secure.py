# The secure.py file stores SECURE_SETTINGS dictionary of environment variables and secrest.
import os

# New migration way, using environment variables, no fallback to old hardcoded values
SECURE_SETTINGS = {
    'enable_debug': os.environ['ENABLE_DEBUG'] == 'True', # non string value, need to be boolean True or False
    'django_secret_key': os.environ['DJANGO_SECRET_KEY'],
    'redis_host': os.environ['REDIS_HOST'],
    'db_default_host': os.environ['DB_HOST'],
    'db_default_name': os.environ['DB_NAME'],
    'db_default_user': os.environ['DB_USER'],
    'db_default_password': os.environ['DB_PASSWORD'],
    'CONSUMER_KEY': os.environ['CONSUMER_KEY'],
    'LTI_SECRET': os.environ['LTI_SECRET'],
    'X_FRAME_OPTIONS': os.environ['X_FRAME_OPTIONS'],
    'help_email_address': os.environ['HELP_EMAIL_ADDRESS'],
    # The remaining values have default, fallback values in code if not set
    'db_default_port': os.environ['DB_PORT'], # default 5432
    'redis_port': os.environ['REDIS_PORT'], # `default 6379    
    'log_level': os.environ['LOG_LEVEL'], # default INFO
    'default_cache_timeout_secs': os.environ['DEFAULT_CACHE_TIMEOUT_SECS'], # default 300
    'log_root': os.environ['LOG_ROOT'], # default /var/opt/django/log/
    'django_settings_module': os.environ['DJANGO_SETTINGS_MODULE'], # default academic_integrity_tool_v2.settings.aws
    'ngrok_domain': os.environ['NGROK_DOMAIN'], # default .ngrok-free.app
    'session_cookie_secure': os.environ['DJANGO_SESSION_COOKIE_SECURE'],
    'session_cookie_samesite': os.environ['DJANGO_SESSION_COOKIE_SAMESITE']
}


