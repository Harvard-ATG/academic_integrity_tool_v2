"""Server-side validation for policy body content (XSS prevention).

This validator is attached to both PolicyTemplates.body and Policies.body via
Django's validators=[] on the model field. It runs automatically during
form.is_valid() and model.full_clean(), but NOT on direct ORM .save() or
.create() — preserving the developer escape hatch for management commands,
fixtures, and shell access.

Two code paths:
  1. Quill Delta JSON (new editor) — parses ops, checks each insert and link
     attribute for script tags and javascript: URIs.
  2. Legacy HTML (existing data / plain text) — checks raw and HTML-decoded
     values for script tags.

The javascript: URI check was added based on Fortinet WAF testing, which
revealed two gaps: `javascript:document.cookie` and `eval(document.cookie)`
pass through the Fortinet Cross-Site-Scripting-02 rule when embedded inside
JSON string values. See waf_testing/WAF_TEST_RESULTS.md for details.
"""

import html
import json
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Matches a complete <script>...</script> block, including multi-line content.
# Handles: <script>alert('xss')</script>, <script type="text/javascript">...</script>, etc.
SCRIPT_BLOCK_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)

# Matches any remaining standalone <script> or </script> tags that weren't part of a
# matched pair above — e.g. an unclosed <script> or a stray </script> with no opener.
# We need both patterns because a malformed/incomplete tag would bypass the block pattern.
SCRIPT_ORPHAN_TAG_PATTERN = re.compile(r'</?script[^>]*>', re.IGNORECASE)

# Matches javascript: URIs (with optional whitespace before colon).
# Covers: javascript:alert(1), javascript:document.cookie, JaVaScRiPt : void(0), etc.
JAVASCRIPT_URI_PATTERN = re.compile(r'javascript\s*:', re.IGNORECASE)


def _contains_script_tags(text):
    """Return True if text contains <script> tags (paired or orphaned)."""
    return bool(SCRIPT_BLOCK_PATTERN.search(text) or SCRIPT_ORPHAN_TAG_PATTERN.search(text))


def _contains_dangerous_uri(text):
    """Return True if text contains javascript: URIs."""
    return bool(JAVASCRIPT_URI_PATTERN.search(text))


def _validate_html_content(value):
    """Validate HTML string for script tags (legacy data path).

    Checks both the raw value and the HTML-decoded value so that
    HTML-entity-encoded script tags (e.g. &lt;script&gt;) are also
    caught. TinyMCE encoded <script> to &lt;script&gt; before
    submitting the form, so without decoding, the encoded form would
    bypass the regex patterns.
    """
    if _contains_script_tags(value):
        raise ValidationError(_('Script tags are not allowed in policy text.'))

    decoded = html.unescape(value)
    if decoded != value and _contains_script_tags(decoded):
        raise ValidationError(_('Script tags are not allowed in policy text.'))


def _validate_quill_delta(value):
    """Validate Quill Delta JSON for XSS payloads.

    Iterates over each Delta op and checks:
      - insert text: script tags (raw and encoded) and javascript: URIs
      - link attribute: javascript: URIs

    These checks cover the two Fortinet WAF gaps found during dev testing:
      1. javascript:document.cookie in link attributes — passed Fortinet
      2. eval(document.cookie) in text — passed Fortinet
    See waf_testing/WAF_TEST_RESULTS.md "XSS-in-JSON" section.
    """
    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        raise ValidationError(_('Invalid policy content format.'))

    ops = data.get('ops')
    if not isinstance(ops, list):
        raise ValidationError(_('Invalid policy content format.'))

    for op in ops:
        insert = op.get('insert', '')
        attrs = op.get('attributes') or {}

        # Check text content for script tags and dangerous URIs
        if isinstance(insert, str):
            if _contains_script_tags(insert):
                raise ValidationError(_('Script tags are not allowed in policy text.'))
            decoded = html.unescape(insert)
            if decoded != insert and _contains_script_tags(decoded):
                raise ValidationError(_('Script tags are not allowed in policy text.'))
            if _contains_dangerous_uri(insert):
                raise ValidationError(_('JavaScript URIs are not allowed in policy text.'))

        # Check link attributes for javascript: URIs
        link = attrs.get('link', '')
        if isinstance(link, str) and _contains_dangerous_uri(link):
            raise ValidationError(_('JavaScript URIs are not allowed in policy text.'))


def validate_no_script_tags(value):
    """Reject content containing script tags or javascript: URIs.

    Entry point for the validator — detects whether the value is Quill Delta
    JSON or legacy HTML/plain text, then delegates to the appropriate checker.

    Attached to model fields via validators=[]. Runs automatically during
    form.is_valid() and model.full_clean(), but NOT on direct ORM .save()
    or .create() — preserving the developer escape hatch.
    """
    # Deferred import to avoid circular dependency (quill_utils imports nothing
    # from validators, but both live in the same app).
    from .quill_utils import is_quill_delta

    if is_quill_delta(value):
        _validate_quill_delta(value)
    else:
        _validate_html_content(value)
