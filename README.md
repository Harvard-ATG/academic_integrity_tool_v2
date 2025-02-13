![Coverage Status](./coverage.svg)

# AI Policy Tool (V2) (Formerly Academic Integrity Policy Tool)

This is a [django](https://www.djangoproject.com/) application that enables instructors to prepare AI policies from templates made by instructional technologists and publish said policies for students to view. It is an LTI tool that is embedded into and launched from the [Canvas LMS](https://www.instructure.com/canvas).

## Installing the tool in the Canvas LMS

Follow the Canvas Admin Guide on [How do I configure an external app for an account using XML?](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-configure-an-external-app-for-an-account-using-XML/ta-p/221). This can be done at either the sub-account level or in a specific canvas course by visiting that course's settings.

The key details you will need include:

- **Consumer key**: obtain this from `academic_integrity_tool_v2/settings/secure.py`
- **Shared secret**: obtain this from `academic_integrity_tool_v2/settings/secure.py`
- **XML configuration**: obtain this from http://localhost:8000/lti/config

Once installed, the tool should be displayed in the left-hand course navigation as **AI Policy**. Note that it may be disabled in the navigation by default, so you may need to manually enable it in the course settings navigation (drag and drop to move to the desired position).

## Developer Notes

The instructions below assume you have [Docker](https://www.docker.com/) installed on your machine.

### Getting setup

Configure django settings:

```
$ cp academic_integrity_tool_v2/settings/secure.py.example academic_integrity_tool_v2/settings/secure.py
$ echo 'SECURE_SETTINGS["db_default_host"] = "db" # for docker' >> academic_integrity_tool_v2/settings/secure.py
$ echo 'SECURE_SETTINGS["redis_host"] = "redis" # for docker' >> academic_integrity_tool_v2/settings/secure.py
```

Run the application:

```
$ docker-compose up
$ docker-compose run web python manage.py migrate
$ docker-compose run web python manage.py loaddata --app policy_wizard boilerplate_policy_templates.yml
```

Open the tool in your web browser to verify it is up and running:

```
open http://localhost:8000
```

### Testing

```
$ docker-compose run web python manage.py test
```

### Update the Coverage Badge

```
$ coverage run --source='.' manage.py test
$ coverage-badge -f -o coverage.svg
```
- Then commit and push the changes!

## Resources

### Original demos

These are demos of the original academic integrity tool and are slightly out of date, but preserved for reference.

- [Installation demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=36644539-1b68-4ce1-acba-acbe015a1930)
- [Admin role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=10b3dc66-21b9-4b14-8e18-acbe015a18c2)
- [Instructor role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=f0216922-3d38-4866-8eca-acbe015a1900)
- [Student role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=87f82679-774f-4b47-92ee-acbe015a188e)