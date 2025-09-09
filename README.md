![Coverage Status](./coverage.svg)

# AI Policy Tool (V2) (Formerly Academic Integrity Policy Tool)

This is a [django](https://www.djangoproject.com/) application that enables instructors to prepare AI policies from templates made by instructional technologists and publish said policies for students to view. It is an LTI tool that is embedded into and launched from the [Canvas LMS](https://www.instructure.com/canvas).

## Installing the tool in the Canvas LMS

Follow the Canvas Admin Guide on [How do I configure an external app for an account using XML?](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-configure-an-external-app-for-an-account-using-XML/ta-p/221). This can be done at either the sub-account level or in a specific canvas course by visiting that course's settings.

The key details you will need include:

- **Consumer key**: obtain this from `academic_integrity_tool_v2/settings/.env`
- **Shared secret**: obtain this from `academic_integrity_tool_v2/settings/.env`
- **XML configuration**: obtain this from http://localhost:8000/lti/config. Or with ngrok, [https://<random-string>.ngrok-free.app/lti/config](https://ngrok.com/docs/universal-gateway/domains/#ngrok-managed-domains)

Once installed, the tool should be displayed in the left-hand course navigation as **AI Policy**. Note that it may be disabled in the navigation by default, so you may need to manually enable it in the course settings navigation (drag and drop to move to the desired position).

## Developer Notes

The instructions below assume you have [Docker](https://www.docker.com/) installed on your machine.

### Getting setup

Configure django settings:

```
$ cp academic_integrity_tool_v2/.env.example academic_integrity_tool_v2/settings/.env

```

Run the application:

```
$ docker compose up

```

Open the tool in your web browser to verify it is up and running:

```
open http://localhost:8000
```

### Testing

```
$ docker compose run web python manage.py test
```

#### Integrated Testing

When this tool is launched from Canvas, it is embedded in an `iframe` from a secure (`https-` based) site. For the cross-domain session and CSRF cookies to function correctly, our Django settings are configured with `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`. These settings command the browser to only send cookies over a secure HTTPS connection.

While local development on `http://localhost:8000` may appear to work for basic views, this is because modern browsers often treat `localhost` as a "secure context" and relax this policy. However, this does not accurately simulate the production LTI environment and will fail when trying to establish a valid cross-domain session.

To properly test the LTI flow locally, you must expose your local development server on a public **HTTPS** URL. **NGROK** is a tool that provides this functionality.

##### NGrok Configuration Steps

1.  **Install NGROK**: Follow the [official instructions](https://ngrok.com/docs/getting-started/)

2.  **Start the Django Server**: Run the local development server as usual.
    ```bash
    docker-compose up
    ```

3.  **Start NGROK**: In a separate terminal, run the following command to expose your local port 8000 on a public HTTPS URL.
    ```bash
    ngrok http --scheme=https 8000
    ```
    -   This command tells `ngrok` to forward traffic to your local `http://localhost:8000` but to set the forwarding scheme in the HTTP headers to `https`. This ensures Django recognizes the connection as secure, which is necessary for the secure cookie flags.

4.  **Update Environment Variables**: NGROK will provide a public URL (ex., `https://<random-string>.ngrok-free.app`).

5.  **Update Canvas**: In your Canvas course settings, [add the LTI tool](https://developerdocs.instructure.com/services/canvas/external-tools/lti/file.tools_xml) using your new public NGROK URL XML page (ex., `https://<random-string>.ngrok-free.app/lti/config`). You can now launch the tool from Canvas to fully test the LTI flow against your local development server with behavior similar to production.


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