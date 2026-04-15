# AGENTS.md

This file provides guidance for coding agents when working with code in this repository.

## Project Overview

Django LTI tool that enables instructors to prepare AI use policies from templates managed by instructional technologists and publish them for students to view. Embedded in and launched from the Canvas LMS via LTI.

**Roles**: Administrator (manages templates) → Instructor (creates/publishes policies from templates) → Student (views published policy)

**Data flow**: LTI launch → Role identification → Template selection → Policy creation/editing → Student viewing

## Commands

**All commands run inside Docker.** Do not install or run Python/Django directly on the host.

```bash
# Start the application
docker compose up

# Run all tests
docker compose run --rm web python manage.py test policy_wizard --settings=academic_integrity_tool_v2.settings.test -v 2

# Run a specific test class
docker compose run --rm web python manage.py test policy_wizard.tests.RoleAndPermissionTests --settings=academic_integrity_tool_v2.settings.test -v 2

# Run a single test
docker compose run --rm web python manage.py test policy_wizard.tests.InstructorRoleTests.testPublishNewPolicy --settings=academic_integrity_tool_v2.settings.test -v 2

# Run migrations
docker compose run --rm web python manage.py migrate

# Load fixture data
docker compose run --rm web python manage.py loaddata boilerplate_policy_templates
```

## Architecture

- **Python 3.6**, **Django 3.2** (runs in Docker)
- **Models**: `PolicyTemplates` (boilerplate templates managed by admins) → `Policies` (course-specific, created by instructors, FK to template)
- **Rich text**: TinyMCE (`django-tinymce`) for `body` fields; output rendered with `|safe` template filter
- **LTI**: `django-lti-provider` for Canvas LMS integration; roles derived from `ext_roles` in LTI launch params
- **Settings**: `base.py` → `local.py` (dev) / `aws.py` (production) / `test.py` (SQLite in-memory)
- **Infrastructure**: Docker Compose with PostgreSQL (dev/prod), Redis (caching), SQLite (tests)

## Key Patterns

- **Role-based access**: Views use `@require_role_instructor`, `@require_role_student`, `@require_role_admin` decorators from `decorators.py`
- **Form validation**: `ModelForm` classes (`NewPolicyForm`, `PolicyTemplateForm`) inherit field validators from model fields automatically
- **Field validators**: `validators=[validate_no_script_tags]` on model `body` fields — runs during `form.is_valid()` and `model.full_clean()` but NOT on direct ORM `save()`/`create()` (by design — developer escape hatch)
- **Fixtures**: `policy_wizard/fixtures/boilerplate_policy_templates.yml` contains all 7 policy templates (PKs 1-7)
- **Template rendering**: All `body` fields use `|safe` in Django templates — server-side validation is the trust boundary

## Testing

Use Django's `unittest`-based `TestCase` with `RequestFactory` for view tests.

```bash
# Run all policy_wizard tests
docker compose run --rm web python manage.py test policy_wizard --settings=academic_integrity_tool_v2.settings.test -v 2

# Run only validation tests
docker compose run --rm web python manage.py test policy_wizard.tests_validations --settings=academic_integrity_tool_v2.settings.test -v 2
```

### Standards

- **Assertions**: Use `assertEqual` (not `assertEquals`). Use `assertTrue`/`assertFalse` for truthy/falsy checks on `SmallIntegerField` boolean flags. Never pass an expected value as the second argument to `assertTrue` — it's the failure message, not a comparison.
- **Fixtures**: Use `fixtures = ['boilerplate_policy_templates']` on test classes that need templates — do not manually create templates in `setUp`.
- **Fixture PKs**: Reference templates by named constants (`MAXIMALLY_RESTRICTIVE_PK`, `MIXED_POLICY_PK`, etc.) defined at the top of `tests.py`, not bare integers.
- **RawPostDataException**: Views with diagnostic logging that access `request.body` after `request.POST` require `mock.patch.object(type(request), 'body', ...)` in tests. The diagnostic logging is marked for removal.
- **Coverage**: Test both the positive case (safe HTML accepted, 302 redirect) and the negative case (script tags rejected, 200 re-render with form errors).

## File Organization

```
policy_wizard/
├── models.py                    # PolicyTemplates, Policies (body fields with validators)
├── validators.py                # validate_no_script_tags (regex-based script tag detection)
├── forms.py                     # NewPolicyForm, PolicyTemplateForm (plain ModelForms)
├── views.py                     # Role-gated views for all CRUD operations
├── decorators.py                # @require_role_* permission decorators
├── roles.py                     # Role constants (ADMINISTRATOR, INSTRUCTOR, STUDENT)
├── utils.py                     # Helper functions (inactivate_active_policies, etc.)
├── urls.py                      # URL routing
├── tests.py                     # LTI launch, role permission, and CRUD tests
├── tests_validations.py             # Script tag validation tests (32 tests)
├── fixtures/
│   └── boilerplate_policy_templates.yml  # 7 policy templates (PKs 1-7)
└── migrations/
```
