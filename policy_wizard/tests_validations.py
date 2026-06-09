"""Tests for script tag validation across all data entry paths.

Verifies that validate_no_script_tags is enforced at the right layers:
- Form validation (is_valid) — BLOCKED — when a ModelForm is submitted and is_valid() is called
- Model full_clean() — BLOCKED — when Django admin saves, or code explicitly calls full_clean()
- View POST submissions — BLOCKED — when instructors/admins submit via the browser (calls is_valid internally)
- Direct ORM save()/create() — NOT BLOCKED (by design) — management commands, shell, fixtures
- QuerySet.update() — NOT BLOCKED (by design) — bulk operations that bypass save() entirely

Tests both legacy HTML content and Quill Delta JSON content.
"""
import json

from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.contrib.sessions.middleware import SessionMiddleware

from .models import Policies, PolicyTemplates
from .forms import NewPolicyForm, PolicyTemplateForm
from .validators import validate_no_script_tags
from . import views


# --- Legacy HTML test data ---

SAFE_HTML = '<p>This policy requires <a href="http://example.com">academic honesty</a>.</p>'
SCRIPT_INLINE = '<p>Hello</p><script>alert("xss")</script>'
SCRIPT_WITH_ATTRS = '<p>Hello</p><script type="text/javascript">document.cookie</script>'
SCRIPT_MULTILINE = '<p>Hello</p><script>\nvar x = 1;\nalert(x);\n</script>'
SCRIPT_ORPHAN_OPEN = '<p>Hello</p><script>alert("no closing tag")'
SCRIPT_ORPHAN_CLOSE = '<p>Hello</p></script>'
SCRIPT_MIXED_CASE = '<p>Hello</p><ScRiPt>alert("xss")</sCrIpT>'
SCRIPT_ENCODED = '<p>Hello</p>&lt;script&gt;alert("xss")&lt;/script&gt;'
SCRIPT_ENCODED_WRAPPED = '<p>&lt;script&gt;alert("xss")&lt;/script&gt;</p>'
SCRIPT_ENCODED_ATTRS = '&lt;script type="text/javascript"&gt;document.cookie&lt;/script&gt;'


# --- Quill Delta test data ---

def _delta(ops):
    return json.dumps({'ops': ops})

DELTA_SAFE_TEXT = _delta([{'insert': 'This is a simple policy.\n'}])
DELTA_SAFE_BOLD = _delta([
    {'insert': 'Important', 'attributes': {'bold': True}},
    {'insert': ': all work must be original.\n'},
])
DELTA_SAFE_LINK = _delta([
    {'insert': 'Honor Code', 'attributes': {'link': 'https://college.harvard.edu/honor-code'}},
    {'insert': '\n'},
])
DELTA_SCRIPT_IN_TEXT = _delta([{'insert': '<script>alert(1)</script>\n'}])
DELTA_ENCODED_SCRIPT = _delta([{'insert': '&lt;script&gt;alert(1)&lt;/script&gt;\n'}])
DELTA_JS_URI_IN_LINK = _delta([
    {'insert': 'click me', 'attributes': {'link': 'javascript:alert(1)'}},
    {'insert': '\n'},
])
DELTA_JS_URI_IN_TEXT = _delta([{'insert': 'javascript:document.cookie\n'}])


def annotate_request_with_session(request, params=None):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    if params is not None:
        for k, v in params.items():
            request.session[k] = v
    return request


class ValidatorUnitTests(TestCase):
    """Direct tests of the validate_no_script_tags function."""

    def test_safe_html_passes(self):
        validate_no_script_tags(SAFE_HTML)

    def test_plain_text_passes(self):
        validate_no_script_tags('No HTML here, just text.')

    def test_inline_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_INLINE)

    def test_script_with_attributes_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_WITH_ATTRS)

    def test_multiline_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_MULTILINE)

    def test_orphan_open_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_ORPHAN_OPEN)

    def test_orphan_close_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_ORPHAN_CLOSE)

    def test_mixed_case_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_MIXED_CASE)

    def test_encoded_script_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_ENCODED)

    def test_encoded_script_wrapped_in_p_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_ENCODED_WRAPPED)

    def test_encoded_script_with_attrs_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(SCRIPT_ENCODED_ATTRS)


class QuillDeltaValidatorTests(TestCase):
    """Tests for Quill Delta JSON validation."""

    def test_safe_text_passes(self):
        validate_no_script_tags(DELTA_SAFE_TEXT)

    def test_safe_bold_passes(self):
        validate_no_script_tags(DELTA_SAFE_BOLD)

    def test_safe_link_passes(self):
        validate_no_script_tags(DELTA_SAFE_LINK)

    def test_script_in_text_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(DELTA_SCRIPT_IN_TEXT)

    def test_encoded_script_in_text_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(DELTA_ENCODED_SCRIPT)

    def test_javascript_uri_in_link_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(DELTA_JS_URI_IN_LINK)

    def test_javascript_uri_in_text_blocked(self):
        with self.assertRaises(ValidationError):
            validate_no_script_tags(DELTA_JS_URI_IN_TEXT)

    def test_non_list_ops_treated_as_plain_text(self):
        """JSON with ops that isn't a list falls through to HTML validation (no XSS = passes)."""
        validate_no_script_tags('{"ops": "not a list"}')

    def test_malformed_delta_treated_as_plain_text(self):
        validate_no_script_tags('{"ops": "broken"}')


class FormValidationTests(TestCase):
    """Tests that form.is_valid() triggers the validator."""

    def test_new_policy_form_rejects_script(self):
        form = NewPolicyForm(data={'body': SCRIPT_INLINE})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_new_policy_form_accepts_safe_html(self):
        form = NewPolicyForm(data={'body': SAFE_HTML})
        self.assertTrue(form.is_valid())

    def test_policy_template_form_rejects_script(self):
        form = PolicyTemplateForm(data={'body': SCRIPT_INLINE})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_policy_template_form_accepts_safe_html(self):
        form = PolicyTemplateForm(data={'body': SAFE_HTML})
        self.assertTrue(form.is_valid())

    def test_error_message_is_user_friendly(self):
        form = NewPolicyForm(data={'body': SCRIPT_INLINE})
        form.is_valid()
        self.assertIn('Script tags are not allowed', form.errors['body'][0])

    def test_new_policy_form_rejects_encoded_script(self):
        form = NewPolicyForm(data={'body': SCRIPT_ENCODED})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_policy_template_form_rejects_encoded_script(self):
        form = PolicyTemplateForm(data={'body': SCRIPT_ENCODED})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_form_accepts_quill_delta(self):
        form = NewPolicyForm(data={'body': DELTA_SAFE_LINK})
        self.assertTrue(form.is_valid())

    def test_form_rejects_quill_delta_with_script(self):
        form = NewPolicyForm(data={'body': DELTA_SCRIPT_IN_TEXT})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_form_rejects_quill_delta_with_js_uri(self):
        form = NewPolicyForm(data={'body': DELTA_JS_URI_IN_LINK})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


class ModelFullCleanTests(TestCase):
    """Tests that model.full_clean() triggers the validator."""

    def setUp(self):
        self.template = PolicyTemplates.objects.create(name='Test Template', body='safe')

    def test_policy_full_clean_rejects_script(self):
        policy = Policies(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=SCRIPT_INLINE,
            related_template=self.template,
        )
        with self.assertRaises(ValidationError):
            policy.full_clean()

    def test_policy_full_clean_accepts_safe_html(self):
        policy = Policies(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=SAFE_HTML,
            related_template=self.template,
        )
        policy.full_clean()

    def test_template_full_clean_rejects_script(self):
        template = PolicyTemplates(name='Test', body=SCRIPT_INLINE)
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_full_clean_accepts_safe_html(self):
        template = PolicyTemplates(name='Test', body=SAFE_HTML)
        template.full_clean()

    def test_policy_full_clean_accepts_quill_delta(self):
        policy = Policies(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=DELTA_SAFE_LINK,
            related_template=self.template,
        )
        policy.full_clean()

    def test_policy_full_clean_rejects_quill_delta_with_script(self):
        policy = Policies(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=DELTA_SCRIPT_IN_TEXT,
            related_template=self.template,
        )
        with self.assertRaises(ValidationError):
            policy.full_clean()


class ORMBypassTests(TestCase):
    """Confirms that direct ORM operations do NOT trigger the validator."""

    def test_policy_save_allows_script(self):
        policy = Policies(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=SCRIPT_INLINE,
        )
        policy.save()
        policy.refresh_from_db()
        self.assertIn('<script>', policy.body)

    def test_policy_create_allows_script(self):
        policy = Policies.objects.create(
            course_id=2,
            context_id='ctx2',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=SCRIPT_INLINE,
        )
        policy.refresh_from_db()
        self.assertIn('<script>', policy.body)

    def test_queryset_update_allows_script(self):
        policy = Policies.objects.create(
            course_id=3,
            context_id='ctx3',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body=SAFE_HTML,
        )
        Policies.objects.filter(pk=policy.pk).update(body=SCRIPT_INLINE)
        policy.refresh_from_db()
        self.assertIn('<script>', policy.body)

    def test_template_save_allows_script(self):
        template = PolicyTemplates(name='Test', body=SCRIPT_INLINE)
        template.save()
        template.refresh_from_db()
        self.assertIn('<script>', template.body)


class ViewSubmissionTests(TestCase):
    """Tests that script tags are blocked when submitted through views."""

    def setUp(self):
        self.factory = RequestFactory()
        self.template = PolicyTemplates.objects.create(
            name='Custom Policy', body='Default body'
        )
        self.policy = Policies.objects.create(
            course_id=1,
            context_id='ctx1',
            is_published=1,
            published_by='test_user',
            is_active=1,
            body='Original policy body',
            related_template=self.template,
        )
        self.instructorSession = {
            'context_id': 'ctx1',
            'lis_person_sourcedid': 'test_user',
            'role': 'Instructor',
            'course_id': 1,
        }
        self.administratorSession = {
            'context_id': 'ctx1',
            'lis_person_sourcedid': 'test_user',
            'role': 'Administrator',
            'course_id': 1,
        }

    def _post_with_session(self, view_func, url_name, session_params, post_data, *args):
        request = self.factory.post(url_name, post_data)
        annotate_request_with_session(request, session_params)
        return view_func(request, *args)

    def test_instructor_new_policy_rejects_script(self):
        response = self._post_with_session(
            views.instructor_level_policy_edit_view,
            'instructor_level_policy_edit',
            self.instructorSession,
            {'body': SCRIPT_INLINE},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Policies.objects.filter(body=SCRIPT_INLINE).exists()
        )

    def test_instructor_new_policy_accepts_safe_html(self):
        response = self._post_with_session(
            views.instructor_level_policy_edit_view,
            'instructor_level_policy_edit',
            self.instructorSession,
            {'body': SAFE_HTML},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Policies.objects.filter(body=SAFE_HTML).exists()
        )

    def test_instructor_new_policy_accepts_quill_delta(self):
        response = self._post_with_session(
            views.instructor_level_policy_edit_view,
            'instructor_level_policy_edit',
            self.instructorSession,
            {'body': DELTA_SAFE_LINK},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Policies.objects.filter(body=DELTA_SAFE_LINK).exists()
        )

    def test_instructor_new_policy_rejects_quill_delta_with_script(self):
        response = self._post_with_session(
            views.instructor_level_policy_edit_view,
            'instructor_level_policy_edit',
            self.instructorSession,
            {'body': DELTA_SCRIPT_IN_TEXT},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Policies.objects.filter(body=DELTA_SCRIPT_IN_TEXT).exists()
        )

    def test_instructor_edit_policy_rejects_script(self):
        response = self._post_with_session(
            views.edit_active_policy,
            'edit_active_policy',
            self.instructorSession,
            {'body': SCRIPT_INLINE},
            self.policy.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.policy.refresh_from_db()
        self.assertEqual(self.policy.body, 'Original policy body')

    def test_admin_template_edit_rejects_script(self):
        response = self._post_with_session(
            views.admin_level_template_edit_view,
            'admin_level_template_edit',
            self.administratorSession,
            {'body': SCRIPT_INLINE},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.template.refresh_from_db()
        self.assertEqual(self.template.body, 'Default body')

    def test_admin_template_edit_rejects_encoded_script(self):
        response = self._post_with_session(
            views.admin_level_template_edit_view,
            'admin_level_template_edit',
            self.administratorSession,
            {'body': SCRIPT_ENCODED},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.template.refresh_from_db()
        self.assertEqual(self.template.body, 'Default body')

    def test_admin_template_edit_accepts_safe_html(self):
        response = self._post_with_session(
            views.admin_level_template_edit_view,
            'admin_level_template_edit',
            self.administratorSession,
            {'body': SAFE_HTML},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 302)
        self.template.refresh_from_db()
        self.assertEqual(self.template.body, SAFE_HTML)

    def test_admin_template_edit_accepts_quill_delta(self):
        response = self._post_with_session(
            views.admin_level_template_edit_view,
            'admin_level_template_edit',
            self.administratorSession,
            {'body': DELTA_SAFE_LINK},
            self.template.pk,
        )
        self.assertEqual(response.status_code, 302)
        self.template.refresh_from_db()
        self.assertEqual(self.template.body, DELTA_SAFE_LINK)
