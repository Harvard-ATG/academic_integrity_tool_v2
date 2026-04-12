![Coverage Status](./coverage.svg)

# AI Policy Tool (V2) (Formerly Academic Integrity Policy Tool)

This is a [django](https://www.djangoproject.com/) application that enables instructors to prepare AI policies from templates made by instructional technologists and publish said policies for students to view. It is an LTI tool that is embedded into and launched from the [Canvas LMS](https://www.instructure.com/canvas).

## Installing the tool in the Canvas LMS

Follow the Canvas Admin Guide on [How do I configure an external app for an account using XML?](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-configure-an-external-app-for-an-account-using-XML/ta-p/221). This can be done at either the sub-account level or in a specific canvas course by visiting that course's settings.

The key details you will need include:

- **Consumer key**: obtain this from `academic_integrity_tool_v2/settings/.env.example`
- **Shared secret**: obtain this from `academic_integrity_tool_v2/settings/.env.example`
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

### Development Workflows

There are two workflows for local development, depending on whether you need Canvas integration.

#### Local + Dev Login (no Canvas / LTI integration)

For UI changes, template rendering, form behavior — anything that doesn't need a real LTI launch.

1. `docker compose up` (or Run and Debug → **"Local + Dev Login"**)
2. Visit a dev login link to seed your session with a role:

| Role | URL |
|------|-----|
| Instructor | http://localhost:8000/dev/login/instructor/ |
| Student | http://localhost:8000/dev/login/student/ |
| Admin | http://localhost:8000/dev/login/admin/ |

You'll be redirected to that role's landing page. Switch roles by clicking a different link. Session persists until you clear cookies.

> **These routes are only registered when `DEBUG=True` and will 404 in production.**

#### Local + Canvas (integrated LTI testing)

For testing the full LTI flow: Canvas launch → ngrok → LTI handshake → role identification → session. Use this to verify cross-domain cookies, secure context behavior, and the actual install/launch experience.

1. Start both services — either manually or from VS Code:
   - **Manual:** `docker compose up` in one terminal, `ngrok http --scheme=https 8000` in another
   - **VS Code:** Run and Debug panel → **"Local + Canvas"** (launches both in parallel)
2. Copy the ngrok HTTPS URL (e.g. `https://<random-string>.ngrok-free.app`)
3. In Canvas course settings, install the LTI tool using the XML config URL: `https://<random-string>.ngrok-free.app/lti/config`
4. Launch the tool from Canvas course navigation — it should appear as **AI Policy**

**Why ngrok is required:** Canvas embeds the tool in an iframe from a secure (`https`) site. Django's `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True` settings require HTTPS for cookies to work. While `localhost` may appear to work (browsers treat it as a secure context), it doesn't simulate the real cross-domain iframe behavior. ngrok's `--scheme=https` flag ensures Django sees a secure connection.

### VS Code Tasks

Pre-configured tasks are available via **Terminal → Run Task** or the **Run and Debug** panel:

| Task | What it does | Workflow |
|------|-------------|----------|
| **Local + Canvas** | `docker compose up` + `ngrok` in parallel | Local + Canvas |
| Docker Compose Up | `docker compose up` (app only) | Local + Dev Login |
| Ngrok | `ngrok http --scheme=https 8000` | Local + Canvas |
| Run All Tests | Full test suite in Docker | — |
| Run Validation Tests | Only `tests_validations.py` | — |
| Docker Compose Down | `docker compose down` | — |

From the **Run and Debug** panel (▶️):
- **"Local + Dev Login"** — starts Docker Compose, then visit a dev login link
- **"Local + Canvas"** — starts Docker Compose + ngrok, then install the tool in Canvas


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