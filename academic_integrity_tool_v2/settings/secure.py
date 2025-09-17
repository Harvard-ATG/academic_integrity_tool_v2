# The secure.py file stores SECURE_SETTINGS dictionary of environment variables and secrets.
import os
from ..utils import parse_env_list

# New migration way: environment-driven SECURE_SETTINGS
# Required (will raise KeyError at import if missing): keep as os.environ[...] to fail-fast
# Optional (have defaults or empty): use os.environ.get(...)

SECURE_SETTINGS = {
    # Secrets (stored in Parameter Store)
    'django_secret_key': os.environ['DJANGO_SECRET_KEY'],  # Django SECRET_KEY (required)
    'CONSUMER_KEY': os.environ['CONSUMER_KEY'],            # LTI consumer key (required)
    'LTI_SECRET': os.environ['LTI_SECRET'],                # LTI shared secret (required)

    # Database connection (host/user/name/port)
    'db_default_host': os.environ['DB_HOST'],              # DB host (required)
    'db_default_port': os.environ.get('DB_PORT', 5432),     # DB port (optional; code falls back to 5432)
    'db_default_name': os.environ['DB_NAME'],              # DB name (required)
    'db_default_user': os.environ['DB_USER'],              # DB user (required)
    'db_default_password': os.environ['DB_PASSWORD'],      # DB password (required)

    # Caching / Redis
    'redis_host': os.environ['REDIS_HOST'],                # Redis host (required)
    'redis_port': os.environ.get('REDIS_PORT', 6379),      # Redis port (optional; default 6379)
    'default_cache_timeout_secs': os.environ.get('DEFAULT_CACHE_TIMEOUT_SECS', 300),
                                                           # cache TTL (optional; default 300)
    # Logging
    'log_level': os.environ.get('LOG_LEVEL', 'INFO'),      # log level (optional; default INFO)

    # Runtime Settings
    'enable_debug': os.environ['ENABLE_DEBUG'] == 'True',  # DEBUG flag (required; 'True' == True)
    'django_settings_module': os.environ['DJANGO_SETTINGS_MODULE'], # which settings module to use (optional)

    # Security Settings
    'ALLOWED_HOSTS': parse_env_list(os.environ['ALLOWED_HOSTS']), # Determine if the split is working correctly
    'X_FRAME_OPTIONS': os.environ['X_FRAME_OPTIONS'], # Security header to prevent clickjacking

    # Session / cookie management
    'session_cookie_secure': os.environ.get('DJANGO_SESSION_COOKIE_SECURE', 'True'), # Use secure cookies
    'session_cookie_samesite': os.environ.get('DJANGO_SESSION_COOKIE_SAMESITE', 'None'), # SameSite attribute for cookies

    # Misc
    'help_email_address': os.environ.get('HELP_EMAIL_ADDRESS', 'help@example.com'),
}
