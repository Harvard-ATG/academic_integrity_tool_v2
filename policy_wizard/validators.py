import html
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


def _contains_script_tags(text):
    """Return True if text contains <script> tags (paired or orphaned)."""
    return bool(SCRIPT_BLOCK_PATTERN.search(text) or SCRIPT_ORPHAN_TAG_PATTERN.search(text))


def validate_no_script_tags(value):
    """Reject HTML containing <script> tags to prevent stored XSS.

    Checks both the raw value and the HTML-decoded value so that
    HTML-entity-encoded script tags (e.g. &lt;script&gt;) are also
    rejected.  TinyMCE encodes <script> to &lt;script&gt; before
    submitting the form, so without decoding, the encoded form would
    bypass the regex patterns.

    Blocks: <script> tags — raw and HTML-entity-encoded, paired and
            orphaned/malformed.
    Allows: all other HTML including <a href>, formatting tags, etc.

    Attached to model fields via validators=[]. Runs automatically during
    form.is_valid() and model.full_clean(), but NOT on direct ORM .save()
    or .create() — preserving the developer escape hatch.
    """
    if _contains_script_tags(value):
        raise ValidationError(_('Script tags are not allowed in policy text.'))

    decoded = html.unescape(value)
    if decoded != value and _contains_script_tags(decoded):
        raise ValidationError(_('Script tags are not allowed in policy text.'))

