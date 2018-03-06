FROM python:3-slim
WORKDIR /app
ADD . /app
RUN apt-get update 
RUN apt-get install -y build-essential
RUN pip3 install -r academic_integrity_tool_v2/requirements/local.txt
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE academic_integrity_tool_v2.settings.local
CMD ["python3", "manage.py", "runserver"]
