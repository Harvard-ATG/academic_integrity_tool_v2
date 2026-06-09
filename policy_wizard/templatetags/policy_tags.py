"""Custom template filter for rendering policy body content.

Usage in templates:
    {% load policy_tags %}
    {{ policy.body|render_body }}

Replaces the previous {{ policy.body|safe }} pattern. The |render_body filter
detects whether the body is Quill Delta JSON (new editor) or legacy HTML
(TinyMCE era) and renders accordingly:
  - Delta JSON → converted to safe HTML via delta_to_html()
  - Legacy HTML → passed through unchanged (backward compatible)

The mark_safe() call is intentional — for Delta JSON, all text content is
HTML-escaped during rendering in quill_utils.py. For legacy HTML, the content
was previously rendered via |safe anyway.
"""

from django import template
from django.utils.safestring import mark_safe

from policy_wizard.quill_utils import render_policy_body

register = template.Library()


@register.filter(name='render_body')
def render_body(value):
    """Render a policy body to HTML, handling both Quill Delta and legacy HTML."""
    return mark_safe(render_policy_body(value))
