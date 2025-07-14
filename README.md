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
$ docker compose up
$ docker compose run web python manage.py migrate
$ docker compose run web python manage.py loaddata --app policy_wizard boilerplate_policy_templates.yml
```

Open the tool in your web browser to verify it is up and running:

```
open http://localhost:8000
```

### Testing

```
$ docker compose run web python manage.py test
```

### Update the Coverage Badge

```
$ coverage run --source='.' manage.py test
$ coverage-badge -f -o coverage.svg
```
- Then commit and push the changes!

## Resources

<details>
<summary><strong>Terraform Migration</strong></summary>


Documents how environment variables and secrets are currently handled via Ansible and S3 (legacy), and how they will be managed after migrating to Terraform/ECS. It also includes practical lookup references to support migration.

#### 1. Current Setup: Ansible + S3

**How It Works**
- **Storage:** All secrets & variables reside in S3 (`tlt-secure-settings`) organized by environment (`dev`, `prod`, etc.).
- **Loading:** The Ansible playbook (`django_deploy.yml` in `tlt-ops/ansible/`) loads these with the `huit-at.s3-vars` role, based on the target environment.
- **Templating:** Templates like `secure.py.j2` or `.env.j2` are rendered with secret values and placed into the Django project.
- **Environment selection:** The deployment command you run specifies which S3 object gets loaded.
- **Injection:** Both secrets (e.g., `DJANGO_SECRET_KEY`, `db_default_password`) and config (e.g., `redis_host`) are injected this way.

#### 2. Migration Plan: Terraform + ECS

- **Secrets:** Will move to AWS Parameter Store or Secrets Manager; ECS tasks fetch them directly.
- **Config variables (non-secrets):** Will be set as environment variables in the Terraform ECS service/task definition.
- **No more S3/Ansible indirection:** Direct injection into container, not via template files.
- **Variable names:** Should remain unchanged during migration.

**Migration Steps**
1. Identify all current environment secrets/configs in S3 for each environment.
2. Migrate secrets to Parameter Store/Secrets Manager.
3. Set non-secrets as environment variables in Terraform.
4. Refactor Django’s config (`secure.py`) to pull settings from OS environment variables (not files).

#### 3. Variable Reference Tables

Here are the environment variables and secrets found in the project, how they are sourced today, and where they should go during migration.

<details>
<summary><strong>Secrets for Param Store</strong></summary>

These variables are considered sensitive and are managed through a secure parameter store.

| Variable Name (Core)   | Secure | Where Set      | Where Consumed (settings file)      | Aliases Powered           | S3 Bucket Source                                   | Param Store Path                                  |
|------------------------|--------|---------------|-------------------------------------|---------------------------|----------------------------------------------------|---------------------------------------------------|
| DJANGO_SECRET_KEY      | Yes    | asgi.py, manage.py | settings/aws.py, settings/local.py | SECRET_KEY                | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/django_secret_key |
| DB_HOST                | Yes    | secure.py     | settings/base.py                    | db_default_host           | tlt-secure-settings/{{env}}/django/atg/settings.yml<br>Points to:<br>tlt-secure-settings/{{env}}/aws.yml<br>aws_postgres_host | /dev/academic_integrity_tool_v2/db_host           |
| DB_PORT                | Yes    | secure.py     | settings/base.py                    | db_default_port           | tlt-secure-settings/{{env}}/django/atg/settings.yml<br>Points to:<br>tlt-secure-settings/{{env}}/aws.yml<br>aws_postgres_port | /dev/academic_integrity_tool_v2/db_port           |
| DB_NAME                | Yes    | secure.py   | settings/base.py                    | db_default_name, POSTGRES_DB | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/db_name           |
| DB_USER                | Yes    | secure.py   | settings/base.py                    | db_default_user, POSTGRES_USER | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/db_user           |
| DB_PASSWORD            | Yes    | secure.py   | settings/base.py                    | db_default_password, POSTGRES_PASSWORD | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/db_password       |
| REDIS_HOST             | Yes    | secure.py     | settings/base.py                    |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml<br>Points to:<br>tlt-secure-settings/{{env}}/aws.yml<br>aws_redis_host | /dev/academic_integrity_tool_v2/redis_host        |
| REDIS_PORT             | Yes    | secure.py     | settings/base.py                    |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml<br>Points to:<br>tlt-secure-settings/{{env}}/aws.yml<br>aws_redis_port | /dev/academic_integrity_tool_v2/redis_port        |
| CONSUMER_KEY           | Yes    | secure.py   | settings/base.py                    |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/consumer_key      |
| LTI_SECRET             | Yes    | secure.py   | settings/base.py                    |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml| /dev/academic_integrity_tool_v2/lti_secret        |
| EMAIL_HOST_PASSWORD    | Yes    | settings/aws.py    | settings/aws.py                     |                           | None Provided                                       | None                                              |

</details>

<details>
<summary><strong>Environment Variables for Terraform</strong></summary>

These variables are typically set as environment variables and are often managed or provisioned via Terraform.

| Variable Name (Core)   | Where Set      | Where Consumed (settings file)      | Dev/Prod/AWS/Other | Aliases Powered           | S3 Bucket Source / From                                 | Dev Value                        | Prod Value                       |
|------------------------|---------------|-------------------------------------|--------------------|---------------------------|---------------------------------------------------------|-----------------------------------|----------------------------------|
| X_FRAME_OPTIONS        | secure.py     | settings/base.py                    | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | 'ALLOW-FROM https://canvas.dev.tlt.harvard.edu/' | 'ALLOW-FROM https://canvas.harvard.edu' |
| DJANGO_SETTINGS_MODULE | env var / compose / manage.py | manage.py, wsgi.py, docker-compose | Dev, Prod, AWS     |                           | Conditions set in wsgi.py, manage.py                    | academic_integrity_tool_v2.settings.aws | academic_integrity_tool_v2.settings.aws |
| HELP_EMAIL_ADDRESS     | secure.py or .env.example | settings/base.py                    | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | atg@fas.harvard.edu              | ithelp@harvard.edu               |
| ENABLE_DEBUG           | secure.py     | settings/aws.py, settings/local.py  | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | True                             | False                            |
| DEFAULT_CACHE_TIMEOUT_SECS | settings/base.py | settings/base.py                    | Dev, Prod, AWS     |                           | None Provided                                            | 300                               | 300                              |
| LOG_LEVEL              | secure.py     | settings/base.py                    | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | DEBUG                            | INFO                             |
| LOG_ROOT               | secure.py     | settings/base.py                    | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | /var/opt/django/log/             | /var/opt/django/log/             |
| EMAIL_HOST_USER        | settings/aws.py| settings/aws.py                     | Dev, Prod, AWS     |                           | tlt-secure-settings/{{env}}/django/atg/settings.yml     | None Provided                                | None Provided                               |
                        |

</details>

<details>
<summary><strong>S3 Bucket/Object Lookup Table</strong></summary>

This table provides the exact S3 bucket and object paths for each environment variable or secret, including any cross-references to other buckets (such as AWS infrastructure values).

| Variable Name      | S3 Bucket/Object Path (Primary)                      | S3 Object Key/Section           | S3 Bucket/Object Path (AWS/Other)                       | S3 Object Key/Section (AWS/Other) | Notes/Instructions                        |
|--------------------|-----------------------------------------------------|-------------------------------|---------------------------------------------------------|-------------------------------|-------------------------------------------|
| DJANGO_SECRET_KEY  | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2     |                                                         |                               | Look for `DJANGO_SECRET_KEY` key          |
| DB_HOST            | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.db_default_host       | tlt-secure-settings/{{env}}/aws.yml                     | aws_postgres_host             | Use value from `aws_postgres_host`        |
| REDIS_HOST         | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.redis_host            | tlt-secure-settings/{{env}}/aws.yml                     | aws_redis_host                 | Use value from `aws_redis_host`           |
| DB_PORT            | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.db_default_port       | tlt-secure-settings/{{env}}/aws.yml                     | aws_postgres_port              | Use value from `aws_postgres_port`        |
| REDIS_PORT         | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.redis_port            | tlt-secure-settings/{{env}}/aws.yml                     | aws_redis_port                 | Use value from `aws_redis_port`           |
| DB_NAME            | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.db_default_name |                                                 |                               | Look for `DB_NAME` or `db_default_name`   |
| DB_USER            | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.db_default_user |                                                 |                               | Look for `DB_USER` or `db_default_user`   |
| DB_PASSWORD        | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.db_default_password |                                         |                               | Look for `DB_PASSWORD` or `db_default_password` |
| CONSUMER_KEY       | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.consumer_key |                                             |                               | Look for `CONSUMER_KEY`                   |
| LTI_SECRET         | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.lti_secret |                                               |                               | Look for `LTI_SECRET`                     |
| X_FRAME_OPTIONS    | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.x_frame_options |                                         |                               | Look for `X_FRAME_OPTIONS`                |
| DJANGO_SETTINGS_MODULE | N/A                                             | N/A                           | N/A                                                    | N/A                           | Set by environment or process             |
| HELP_EMAIL_ADDRESS | tlt-secure-settings/{{env}}/django/atg/settings.yml | academic_integrity_tool_v2.help_email_address |                                 |                               | Look for `HELP_EMAIL_ADDRESS`             |
| ENABLE_DEBUG       | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.enable_debug           |                                                 |                               | Look for `ENABLE_DEBUG`                   |
| LOG_LEVEL          | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.log_level              |                                                 |                               | Look for `LOG_LEVEL`                      |
| LOG_ROOT           | tlt-secure-settings/{{env}}/django/atg/settings.yml | defaults.log_root               |                                                 |                               | Look for `LOG_ROOT`                       |
> **Note:**  
> `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are not managed via S3.  
> - `EMAIL_HOST_USER` is set in `settings/aws.py`.  
> - `EMAIL_HOST_PASSWORD` is set in `settings/aws.py` or via environment variable in production.

> **Tip:**  
> For each variable, check the primary S3 object first. If the value is a reference (e.g., `defaults.db_default_host`), follow the pointer to the AWS S3 object and use the value from the referenced key.

</details>

</details>


### Original demos

These are demos of the original academic integrity tool and are slightly out of date, but preserved for reference.

- [Installation demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=36644539-1b68-4ce1-acba-acbe015a1930)
- [Admin role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=10b3dc66-21b9-4b14-8e18-acbe015a18c2)
- [Instructor role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=f0216922-3d38-4866-8eca-acbe015a1900)
- [Student role demo](https://harvard.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=87f82679-774f-4b47-92ee-acbe015a188e)