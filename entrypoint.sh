#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- DEBUGGING LINE ---
echo "DJANGO_SETTINGS_MODULE is set to: $DJANGO_SETTINGS_MODULE"
# --- END DEBUGGING LINE ---

# Local only: Wait for the database service to be available. Not needed in dev/prod using long running services.
if [[ "$DJANGO_SETTINGS_MODULE" == *"local"* ]]; then
    echo "Waiting for database to be ready..."
    /usr/local/bin/docker-wait-for-it.sh db:5432 --timeout=60 --strict --
fi

# Run database migrations without interactive prompts (i.e --no-input)
echo "Applying Django database migrations..."
python manage.py migrate --no-input

# Local only: load initial data based on the Django settings module. Not needed in dev/prod.
if [[ "$DJANGO_SETTINGS_MODULE" == *"local"* ]]; then
    echo "Loading initial data..."
    python manage.py loaddata --app policy_wizard boilerplate_policy_templates.yml
fi

# Execute the main command from the Dockerfile's CMD.
# This passes control to the real application and executes the startup command.
echo "Starting application..."
exec "$@"
