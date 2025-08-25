FROM python:3.6
WORKDIR /app
RUN mkdir -p /var/opt/django/log
ADD . /app
RUN pip3 install -r academic_integrity_tool_v2/requirements/local.txt
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE academic_integrity_tool_v2.settings.local
CMD ["python3", "manage.py", "runserver"]
