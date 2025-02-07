[![Build Status](https://travis-ci.org/Harvard-ATG/academic_integrity_tool_v2.svg?branch=master)](https://travis-ci.org/Harvard-ATG/academic_integrity_tool_v2)
![Coverage Status](./coverage.svg)

# AI Policy Tool (V2) (Formerly Academic Integrity Policy Tool)

This is a django application that enables instructors to prepare academic integrity policies from templates made by instructional technologists and publish said policies for students to view. It is an LTI tool that is embedded into and launched from the Canvas LMS.

## Demos of how the tool works
- [Installation demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=36644539-1b68-4ce1-acba-acbe015a1930)
- [Admin role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=10b3dc66-21b9-4b14-8e18-acbe015a18c2)
- [Instructor role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=f0216922-3d38-4866-8eca-acbe015a1900)
- [Student role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=87f82679-774f-4b47-92ee-acbe015a188e)

## Steps to get it running locally

### With Vagrant

* Ensure you have [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/) installed on your local machine
* Clone this repository to a desired directory location on your local machine
* From the CLI and in the project root directory, which should contain a `Vagrantfile`, run `vagrant up`
* Log into the local VM with `vagrant ssh`
* Do `workon academic_integrity_tool_v2`
* Run `./manage.py runserver 0.0.0.0:8000`
* Open your browser and navigate to `http://localhost:8000`

### With Docker

* Ensure you have [Docker](https://www.docker.com/) installed on your local machine
* Clone this repository to a desired directory location on your local machine
* Do `cp academic_integrity_v2/settings/secure.py.example academic_integrity_v2/settings/secure.py` and then update:
	- `db_default_host: 'db'` 
	- `redis_host: 'redis'`
* From the CLI and in the project root directory, which should container a `Dockerfile` and `docker-compose.yml` file, run `docker-compose up`
* Open your browser and navigate to `http://localhost:8000`

## Installing the tool in the Canvas LMS:**

* Log into your Harvard Canvas account and select a desired course
* On the left navigation bar, go to "Settings"
* From top horizontal bar, click "Apps"
* Click the blue "App" button. An "Add App" form should pop up.
* On the form, on the "Configuration Type" drop down menu, select "Paste XML". The form structure will update accordingly.
* In the ‘Name’ field, enter "AI Policy".
* For the 'Consumer Key' and 'Shared Secret' fields, use the values in `academic_integrity_tool_v2/academic_integrity_tool_v2/settings/secure.py`
* On a new browser tab, go to 'http://localhost:8000/lti/config'
* Copy the XML output
* Go back to your browser tab with the "Add App" form, In the ‘XML Configuration’ field, paste in the XML output you copied in the step above.
* Change the 5th-to-last line of the XML you just pasted in from
<lticm:property name="default">disabled</lticm:property>
to
<lticm:property name="default">enabled</lticm:property>
* Click the blue "Submit" button.
* You should see the tool listed as "Academic Integrity Tool" in the left navigation pane of Canvas.
* Click that "Academic Integrity Tool" navigation item to launch the tool

## Developer Notes

### Running Tests

With vagrant: 

```
$ vagrant ssh 
$ cd /vagrant 
$ python manage.py test
```

With docker: 

```
$ docker-compose up
$ docker-compose run web python manage.py test
```

### Loading Boilerplate Policy Templates

```
$ python manage.py loaddata --app policy_wizard boilerplate_policy_templates.yml
```


### Update the Coverage Badge ###

```
$ coverage run --source='.' manage.py test
$ coverage-badge -f -o coverage.svg
```
- Then commit and push the changes!