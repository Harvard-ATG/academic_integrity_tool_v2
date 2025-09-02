#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- DEBUGGING LINE ---
echo "DJANGO_SETTINGS_MODULE is set to: $DJANGO_SETTINGS_MODULE"
# --- END DEBUGGING LINE ---

# Wait for the database service to be available, but only in a local environment.
if [[ "$DJANGO_SETTINGS_MODULE" == *"local"* ]]; then
    echo "Waiting for database to be ready..."
    /usr/local/bin/docker-wait-for-it.sh db:5432 --timeout=60 --strict --
fi

# Always run database migrations. The --no-input flag prevents interactive prompts.
echo "Applying Django database migrations..."
python manage.py migrate --no-input

# Conditionally load initial data based on the Django settings module.
if [[ "$DJANGO_SETTINGS_MODULE" == *"local"* ]]; then
    echo "Loading initial data..."
    python manage.py loaddata --app policy_wizard boilerplate_policy_templates.yml
fi

# Execute the main command from the Dockerfile's CMD.
# This ensures that our entrypoint script is a universal wrapper around the
# real application startup command.
echo "Starting application..."
exec "$@"
