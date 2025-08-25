# The secure.py file stores environment specific settings and secrets.  It is
# generated during deployment to AWS based on settings stored in s3.  Using the
# below secure settings in combination with project defaults should be
# sufficient to get you started.  Make sure you copy this file over as is to
# secure.py before running `vagrant up`.

# For migration, will try to pull in environment variables here first.
import os

# old way, commented out
# SECURE_SETTINGS = {
#     'enable_debug': True, # non string value, need to be boolean True or False
#     'django_secret_key': '1@7&11tb*l1c84uco-9=%(u#mb)_dl6%%++rihgnl&r)wmldrc',
#     'redis_host': '127.0.0.1',
#     'db_default_host': '127.0.0.1',
#     'db_default_name': 'academic_integrity_tool_v2',
#     'db_default_user': 'academic_integrity_tool_v2',
#     'db_default_password': 'academic_integrity_tool_v2',
#     'CONSUMER_KEY': 'academic_integrity_tool_v2',
#     'LTI_SECRET': 'secret',
#     'X_FRAME_OPTIONS': 'ALLOW-FROM https://canvas.dev.tlt.harvard.edu/',
#     'help_email_address': 'atg@fas.harvard.edu'
# }
# SECURE_SETTINGS["db_default_host"] = "db" # for docker
# SECURE_SETTINGS["redis_host"] = "redis" # for docker

# # These are the new values from terraform, to be used as environment variables in ECS task definition:
#       environment = [
#         { "name" : "X_FRAME_OPTIONS", "valueFrom" : "${local.ssm_root}/x_frame_options" }, # needs to be ssm param store, dev value - ALLOW-FROM https://canvas.dev.tlt.harvard.edu/, check how this stringw ill be handled in code. Code Check = OK, its a string. x
#         { "name" : "LOG_LEVEL", "valueFrom" : "${local.ssm_root}/log_level"}, # ssm param store - debug / info - DEBUG in all caps, check code. Figure out Handling x
#         { "name" : "HELP_EMAIL_ADDRESS", "valueFrom" : "${local.ssm_root}/help_email_address" }, # ssm param store - atg@fas.harvard.edu - check code. Code check = OK. x
#         { "name" : "ENABLE_DEBUG", "valueFrom" : "${local.ssm_root}/enable_debug" }, # ssm param store, dev value - "True" - Check code. Figure out handling. x
#         { "name" : "DEFAULT_CACHE_TIMEOUT_SECS", "value" : "300" }, # done x
#         { "name" : "DJANGO_SETTINGS_MODULE", "value" : "academic_integrity_tool_v2.settings.aws" }, # done, x
#         { "name" : "LOG_ROOT", "value" : " /var/opt/django/log/" }, # done, x 
#       ]
#       secrets = [
#         { "name" : "DJANGO_SECRET_KEY", "valueFrom" : "${local.ssm_root}/django_secret_key" }, x
#         { "name" : "DB_HOST", "valueFrom" : "${local.ssm_root}/db_host" }, x``
#         { "name" : "DB_PORT", "valueFrom" : "${local.ssm_root}/db_port" }, x
#         { "name" : "DB_NAME", "valueFrom" : "${local.ssm_root}/db_name" }, x 
#         { "name" : "DB_USER", "valueFrom" : "${local.ssm_root}/db_user" }, x 
#         { "name" : "DB_PASSWORD", "valueFrom" : "${local.ssm_root}/db_password" },
#         { "name" : "REDIS_HOST", "valueFrom" : "${local.ssm_root}/redis_host" }, x 
#         { "name" : "REDIS_PORT", "valueFrom" : "${local.ssm_root}/redis_port" }, x 
#         { "name" : "CONSUMER_KEY", "valueFrom" : "${local.ssm_root}/consumer_key" }, x 
#         { "name" : "LTI_SECRET", "valueFrom" : "${local.ssm_root}/lti_secret" }, x
#       ]


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
    # The remaing values no already in this list are:
    'db_default_port': os.environ['DB_PORT'], # not used in code, using default 5432
    'redis_port': os.environ['REDIS_PORT'], # not used in code, using default 6379    
    'log_level': os.environ['LOG_LEVEL'], # not used in code, using default INFO
    'default_cache_timeout_secs': os.environ['DEFAULT_CACHE_TIMEOUT_SECS'], # not used in code, using default 300
    'log_root': os.environ['LOG_ROOT'], # not used in code, using default /var/opt/django/log/
    'django_settings_module': os.environ['DJANGO_SETTINGS_MODULE'], # not used in code, using default academic_integrity_tool_v2.settings.aws
    # 'db_default_engine': 'django.db.backends.postgresql', # not used in code, using default
    # 'email_host_user': os.environ.get('EMAIL_HOST_USER', ''), # not used in code, using default '
    # 'email_host_password': os.environ.get('EMAIL_HOST_PASSWORD', ''), # not used in code, using default '
    # 'email_backend': 'django.core.mail.backends.smtp.EmailBackend', # not used in code, using default
    # 'email_host': 'email-smtp.us-east-1.amazonaws.com', # not used in code, using default
    # 'email_use_tls': True, # not used in code, using default
    # 'email_port': 587, # not used in code, using default
    # 'email_timeout': 5, # not used in code, using default
    # 'default_from_email': os.environ.get('HELP_EMAIL_ADDRESS', '
}
# The following two lines are for docker, comment them out if not using docker, docker needs these values because it uses service names to connect
# Locally these names should match the ones in the docker-compose.yml file but when deployed to AWS they will be replaced by the actual hostnames or IP addresses of the services
# SECURE_SETTINGS["db_default_host"] = "db" # for docker
# SECURE_SETTINGS["redis_host"] = "redis" # for docker

