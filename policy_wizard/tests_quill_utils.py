"""Tests for Quill Delta to HTML rendering."""
import json

from django.test import TestCase

from .quill_utils import delta_to_html, is_quill_delta, render_policy_body


def _delta(ops):
    return json.dumps({'ops': ops})


class IsQuillDeltaTests(TestCase):

    def test_valid_delta(self):
        self.assertTrue(is_quill_delta(_delta([{'insert': 'hello\n'}])))

    def test_plain_html(self):
        self.assertFalse(is_quill_delta('<p>hello</p>'))

    def test_plain_text(self):
        self.assertFalse(is_quill_delta('just text'))

    def test_empty_string(self):
        self.assertFalse(is_quill_delta(''))

    def test_json_without_ops(self):
        self.assertFalse(is_quill_delta('{"foo": "bar"}'))

    def test_not_a_string(self):
        self.assertFalse(is_quill_delta(42))


class DeltaToHtmlTests(TestCase):

    def test_plain_text(self):
        result = delta_to_html(_delta([{'insert': 'Hello world\n'}]))
        self.assertEqual(result, '<p>Hello world</p>')

    def test_bold_text(self):
        result = delta_to_html(_delta([
            {'insert': 'Bold', 'attributes': {'bold': True}},
            {'insert': ' normal\n'},
        ]))
        self.assertEqual(result, '<p><strong>Bold</strong> normal</p>')

    def test_italic_text(self):
        result = delta_to_html(_delta([
            {'insert': 'Italic', 'attributes': {'italic': True}},
            {'insert': '\n'},
        ]))
        self.assertEqual(result, '<p><em>Italic</em></p>')

    def test_underline_text(self):
        result = delta_to_html(_delta([
            {'insert': 'Underlined', 'attributes': {'underline': True}},
            {'insert': '\n'},
        ]))
        self.assertEqual(result, '<p><u>Underlined</u></p>')

    def test_link(self):
        result = delta_to_html(_delta([
            {'insert': 'Honor Code', 'attributes': {'link': 'https://harvard.edu'}},
            {'insert': '\n'},
        ]))
        self.assertEqual(
            result,
            '<p><a href="https://harvard.edu" target="_blank" rel="noopener">Honor Code</a></p>'
        )

    def test_javascript_uri_rejected(self):
        result = delta_to_html(_delta([
            {'insert': 'click', 'attributes': {'link': 'javascript:alert(1)'}},
            {'insert': '\n'},
        ]))
        self.assertNotIn('javascript:', result)
        self.assertNotIn('<a', result)

    def test_header(self):
        result = delta_to_html(_delta([
            {'insert': 'Title'},
            {'insert': '\n', 'attributes': {'header': 1}},
        ]))
        self.assertEqual(result, '<h1>Title</h1>')

    def test_ordered_list(self):
        result = delta_to_html(_delta([
            {'insert': 'First'},
            {'insert': '\n', 'attributes': {'list': 'ordered'}},
            {'insert': 'Second'},
            {'insert': '\n', 'attributes': {'list': 'ordered'}},
        ]))
        self.assertEqual(result, '<ol><li>First</li><li>Second</li></ol>')

    def test_bullet_list(self):
        result = delta_to_html(_delta([
            {'insert': 'Apples'},
            {'insert': '\n', 'attributes': {'list': 'bullet'}},
            {'insert': 'Oranges'},
            {'insert': '\n', 'attributes': {'list': 'bullet'}},
        ]))
        self.assertEqual(result, '<ul><li>Apples</li><li>Oranges</li></ul>')

    def test_blockquote(self):
        result = delta_to_html(_delta([
            {'insert': 'A quote'},
            {'insert': '\n', 'attributes': {'blockquote': True}},
        ]))
        self.assertEqual(result, '<blockquote>A quote</blockquote>')

    def test_text_alignment(self):
        result = delta_to_html(_delta([
            {'insert': 'Centered'},
            {'insert': '\n', 'attributes': {'align': 'center'}},
        ]))
        self.assertEqual(result, '<p style="text-align: center">Centered</p>')

    def test_xss_in_text_is_escaped(self):
        result = delta_to_html(_delta([
            {'insert': '<script>alert(1)</script>\n'},
        ]))
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_image_embed(self):
        result = delta_to_html(_delta([
            {'insert': {'image': 'https://example.com/img.png'}},
            {'insert': '\n'},
        ]))
        self.assertIn('<img src="https://example.com/img.png">', result)

    def test_multiple_paragraphs(self):
        result = delta_to_html(_delta([
            {'insert': 'First paragraph\nSecond paragraph\n'},
        ]))
        self.assertIn('<p>First paragraph</p>', result)
        self.assertIn('<p>Second paragraph</p>', result)

    def test_combined_attributes(self):
        result = delta_to_html(_delta([
            {'insert': 'Bold italic', 'attributes': {'bold': True, 'italic': True}},
            {'insert': '\n'},
        ]))
        self.assertIn('<strong>', result)
        self.assertIn('<em>', result)

    def test_invalid_json(self):
        self.assertEqual(delta_to_html('not json'), '')

    def test_empty_ops(self):
        self.assertEqual(delta_to_html('{"ops": []}'), '')


class RenderPolicyBodyTests(TestCase):

    def test_renders_legacy_html_unchanged(self):
        html = '<p>Legacy <a href="https://example.com">content</a></p>'
        self.assertEqual(render_policy_body(html), html)

    def test_renders_quill_delta_to_html(self):
        delta = _delta([{'insert': 'New content\n'}])
        self.assertEqual(render_policy_body(delta), '<p>New content</p>')

    def test_renders_plain_text_unchanged(self):
        self.assertEqual(render_policy_body('Just text'), 'Just text')
