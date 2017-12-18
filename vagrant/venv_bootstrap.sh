#!/bin/bash
# Set up virtualenv and migrate project
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /home/vagrant/AcademicIntegrityToolV2 -r /home/vagrant/AcademicIntegrityToolV2/AcademicIntegrityToolV2/requirements/local.txt AcademicIntegrityToolV2 
workon AcademicIntegrityToolV2
python manage.py migrate
