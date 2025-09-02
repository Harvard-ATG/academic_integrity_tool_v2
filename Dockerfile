FROM python:3.6
WORKDIR /app
RUN mkdir -p /var/opt/django/log/ && chmod 777 /var/opt/django/log/
# Create the actual log file that Django expects
RUN touch /var/opt/django/log/django-academic_integrity_tool_v2.log && chmod 666 /var/opt/django/log/django-academic_integrity_tool_v2.log
ADD . /app
RUN pip3 install -r academic_integrity_tool_v2/requirements/local.txt
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE academic_integrity_tool_v2.settings.local

# Add the entrypoint script to the container and make it executable.
COPY docker-wait-for-it.sh /usr/local/bin/docker-wait-for-it.sh
RUN chmod +x /usr/local/bin/docker-wait-for-it.sh

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint to the new script. This command will run first when the container starts.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# The CMD is the command that the entrypoint script will execute after all the setup is complete.
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
