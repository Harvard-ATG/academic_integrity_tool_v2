Academic Integrity Policy Tool (V2)

This is a django application that enables instructors to prepare academic integrity policies from templates made by instructional technologists and publish said policies for students to view. It is an LTI tool that is embedded into and launched from the Canvas LMS.

Steps to get it running locally:
* Ensure you have VirtualBox installed on your local machine
* Clone this repository to a desired directory location on your local machine
* From the CLI and in the project root directory, which should contain a Vagrantfile, run `vagrant up`
* Log into the local VM with `vagrant ssh`
* Do `workon academic_integrity_tool_v2`
* Run `./manage.py runserver 0.0.0.0:8000`

Installing the tool in the Canvas LMS:
* Log into your Harvard Canvas account and select a desired course
* On the left navigation bar, go to “Settings”
* From top horizontal bar, click “Apps”
* Click the blue “App” button. An “Add App” form should pop up.
* On the form, on the “Configuration Type” drop down menu, select “Paste XML”. The form structure will update accordingly.
* In the ‘Name’ field, type “Academic Integrity Tool”, without the quotation marks.
* For the 'Consumer Key' and 'Shared Secret' fields, from a new CLI window, access and use the values in academic_integrity_tool_v2/academic_integrity_tool_v2/settings/secure.py
* On a new browser tab, go to 'localhost:8000/lti/config.xml'
* Copy the XML output
* Go back to your browser tab with the “Add App” form, In the ‘XML Configuration’ field, paste in the XML output you copied in the step above.
* Change the 5th-to-last line of the XML you just pasted in from
<lticm:property name="default">disabled</lticm:property>
to
<lticm:property name="default">enabled</lticm:property>
* Click the blue “Submit” button.
* You should see the tool listed as “Academic Integrity Tool” in the left navigation pane of Canvas.
* Click that "Academic Integrity Tool" navigation item to launch the tool
