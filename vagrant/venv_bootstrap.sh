#!/bin/bash
# Set up virtualenv and migrate project
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv --python=python3 -a /home/vagrant/academic_integrity_tool_v2 -r /home/vagrant/academic_integrity_tool_v2/academic_integrity_tool_v2/requirements/local.txt academic_integrity_tool_v2
workon academic_integrity_tool_v2
python manage.py migrate
