foo
django-project-template
=======================

Use this template to create a new Django project like this:

django-admin.py startproject _projectname_ --template=https://github.com/Harvard-University-iCommons/django-project-template/archive/stable/v1.10.x.zip --extension=py,pp,sh,example

## Customizations

* For production deployments, static assets from all app-level static directories are collected into a project level `http_static` directory, which is ignored by git.
* Added `settings` and `requirements` directories under the project subdirectory.
* Default to using a postgres db (installed on local VM via `vagrant up`) with
username, db name, and password defaulting to the project name
* Default to including a redis cache (installed on local VM via `vagrant up`)
