#!/bin/bash

# This is a helpful script to initialize the Django application environment
# It determines the environment (i.e. local or production) and sets up accordingly.
# This includes waiting for services to be available and applying database migrations.
# Additionally, for the local environment, it may load initial data or perform other
# environment-specific tasks.

# Exit immediately if a command exits with a non-zero status.
set -e

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
echo "Starting Django Server application..."

# Local only: print dev login URLs for quick access without Canvas/LTI.
if [[ "$DJANGO_SETTINGS_MODULE" == *"local"* ]]; then
    echo ""
    echo "App is up — migrations applied, fixtures loaded. Try these in your browser:"
    echo ""
    echo "  Instructor: http://localhost:8000/dev/login/instructor/"
    echo "  Student:    http://localhost:8000/dev/login/student/"
    echo "  Admin:      http://localhost:8000/dev/login/admin/"
    echo ""
fi

exec "$@" # Replaces the shell with the Django server process
