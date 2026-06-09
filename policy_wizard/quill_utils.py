"""Server-side Quill Delta JSON to HTML renderer.

Why this exists:
  The Quill editor stores content as Delta JSON — an array of insert operations
  with formatting attributes. Unlike TinyMCE which submitted raw HTML in POST
  bodies (triggering the Fortinet WAF's Cross-Site-Scripting-02 rule), Quill's
  Delta JSON format passes through the WAF because it contains no HTML tags.

  This module converts Delta JSON back to safe HTML for display in templates.
  It also provides format detection so that legacy HTML content (existing data
  in the database from the TinyMCE era) is passed through unchanged.

How it works:
  1. is_quill_delta() — detects whether a string is Delta JSON or legacy HTML
  2. render_policy_body() — entry point: routes to delta_to_html() or passthrough
  3. delta_to_html() — splits ops into lines, renders block and inline elements

Security:
  - All text content is HTML-escaped via html.escape() before output
  - javascript:, data:, and vbscript: URIs in links are rejected
  - Embeds (images/video) have their src attributes escaped
  - This is defense-in-depth; the validator (validators.py) catches XSS before
    content is ever saved to the database

Delta format reference: https://quilljs.com/docs/delta/
"""

import json
from html import escape


def is_quill_delta(value):
    """Return True if value is a Quill Delta JSON string.

    A valid Delta is a JSON object with an 'ops' key containing a list.
    Example: {"ops": [{"insert": "Hello world\\n"}]}
    """
    if not isinstance(value, str):
        return False
    try:
        data = json.loads(value)
        return isinstance(data, dict) and isinstance(data.get('ops'), list)
    except (json.JSONDecodeError, TypeError):
        return False


def render_policy_body(value):
    """Render policy body content to HTML.

    This is the main entry point, called by the |render_body template filter.
    Routes to delta_to_html() for Quill Delta JSON, or returns the value
    unchanged for legacy HTML/plain text (backward compatible with existing
    data from the TinyMCE era).
    """
    if is_quill_delta(value):
        return delta_to_html(value)
    # Legacy HTML or plain text — pass through unchanged.
    # Existing data in the database was already saved as HTML by TinyMCE.
    return value


def delta_to_html(value):
    """Convert a Quill Delta JSON string to safe HTML.

    Processing pipeline:
      1. Parse JSON and extract ops list
      2. Split ops into lines (each line = inline spans + block attributes)
      3. Render lines to HTML (paragraphs, headers, lists, blockquotes)
    """
    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return ''

    ops = data.get('ops')
    if not isinstance(ops, list):
        return ''

    lines = _split_into_lines(ops)
    return _lines_to_html(lines)


def _split_into_lines(ops):
    """Split Delta ops into lines, each with inline spans and block attributes.

    In Quill Delta format, a newline character "\\n" terminates a line, and any
    attributes on that newline op are BLOCK-level attributes (header, list, align).
    Inline attributes (bold, italic, link) live on the text ops within the line.

    Returns list of (inlines, block_attrs) tuples. Each inline is a
    (type, content, attrs) tuple where type is 'text' or 'embed'.
    """
    lines = []
    current = []

    for op in ops:
        insert = op.get('insert', '')
        attrs = op.get('attributes') or {}

        # Embeds (images, videos) are dicts, not strings
        if isinstance(insert, dict):
            current.append(('embed', insert, attrs))
            continue

        text = str(insert)

        # A bare newline terminates the current line;
        # its attributes are the block-level format for that line
        if text == '\n':
            lines.append((list(current), attrs))
            current = []
            continue

        # Text may contain embedded newlines (e.g. pasted multi-line text).
        # Split them into separate lines, each inheriting inline attrs.
        parts = text.split('\n')
        for i, part in enumerate(parts):
            if part:
                current.append(('text', part, attrs))
            if i < len(parts) - 1:
                # Mid-text newline — terminates a line with no block attrs
                lines.append((list(current), {}))
                current = []

    # Trailing content without a final newline
    if current:
        lines.append((current, {}))

    return lines


def _lines_to_html(lines):
    """Convert lines to HTML, grouping consecutive list items.

    Block-level rendering rules:
      - header: 1-6 → <h1>-<h6>
      - list: 'ordered' → <ol>, 'bullet' → <ul>  (consecutive items grouped)
      - blockquote: True → <blockquote>
      - align: center/right/justify → <p style="text-align: ...">
      - default → <p>
    """
    result = []
    i = 0

    while i < len(lines):
        inlines, block_attrs = lines[i]
        inner = _render_inlines(inlines)

        # Group consecutive list items into a single <ol> or <ul>
        list_type = block_attrs.get('list')
        if list_type:
            tag = 'ol' if list_type == 'ordered' else 'ul'
            items = [f'<li>{inner}</li>']
            j = i + 1
            while j < len(lines):
                next_inlines, next_attrs = lines[j]
                if next_attrs.get('list') == list_type:
                    items.append(f'<li>{_render_inlines(next_inlines)}</li>')
                    j += 1
                else:
                    break
            result.append(f'<{tag}>{"".join(items)}</{tag}>')
            i = j
            continue

        header = block_attrs.get('header')
        if header and isinstance(header, int) and 1 <= header <= 6:
            result.append(f'<h{header}>{inner}</h{header}>')
        elif block_attrs.get('blockquote'):
            result.append(f'<blockquote>{inner}</blockquote>')
        elif inner:
            align = block_attrs.get('align')
            if align in ('center', 'right', 'justify'):
                result.append(f'<p style="text-align: {align}">{inner}</p>')
            else:
                result.append(f'<p>{inner}</p>')

        i += 1

    return '\n'.join(result)


def _render_inlines(inlines):
    """Render a list of inline spans to HTML."""
    return ''.join(_render_one(*item) for item in inlines)


def _render_one(kind, content, attrs):
    """Render a single inline element to HTML.

    All text content is HTML-escaped before wrapping in formatting tags.
    Inline attributes are applied inside-out: bold, italic, underline,
    strike, superscript/subscript, then link as the outermost wrapper.
    """
    if kind == 'embed':
        return _render_embed(content)

    # Escape text to prevent XSS — this is the primary safety gate
    html = escape(str(content))

    # Apply inline formatting attributes
    if attrs.get('bold'):
        html = f'<strong>{html}</strong>'
    if attrs.get('italic'):
        html = f'<em>{html}</em>'
    if attrs.get('underline'):
        html = f'<u>{html}</u>'
    if attrs.get('strike'):
        html = f'<s>{html}</s>'
    if attrs.get('script') == 'super':
        html = f'<sup>{html}</sup>'
    if attrs.get('script') == 'sub':
        html = f'<sub>{html}</sub>'

    # Wrap in link if present and safe
    link = attrs.get('link')
    if link and _is_safe_url(link):
        href = escape(_normalize_url(link), quote=True)
        html = f'<a href="{href}" target="_blank" rel="noopener">{html}</a>'

    return html


def _render_embed(content):
    """Render an embed (image or video) to HTML.

    Quill represents embeds as dicts: {"image": "url"} or {"video": "url"}.
    Both src attributes are HTML-escaped to prevent attribute injection.
    """
    if not isinstance(content, dict):
        return ''
    if 'image' in content:
        src = escape(str(content['image']), quote=True)
        return f'<img src="{src}">'
    if 'video' in content:
        src = escape(str(content['video']), quote=True)
        return f'<iframe src="{src}" frameborder="0" allowfullscreen></iframe>'
    return ''


def _normalize_url(url):
    """Ensure URLs have a scheme so browsers don't treat them as relative paths.

    Without a scheme, 'www.example.com' renders as a relative href and the
    browser resolves it against the current page (e.g. localhost:8000/.../www.example.com).
    """
    stripped = url.strip()
    if stripped.lower().startswith(('http://', 'https://', 'mailto:', '/', '#')):
        return stripped
    if stripped.lower().startswith('www.'):
        return f'https://{stripped}'
    return stripped


def _is_safe_url(url):
    """Reject javascript:, data:, and vbscript: URIs.

    This is defense-in-depth — the validator (validators.py) already rejects
    these before content reaches the database, but we check again at render
    time in case content was inserted via the ORM escape hatch.
    """
    normalized = url.strip().lower()
    return not normalized.startswith(('javascript:', 'data:', 'vbscript:'))
