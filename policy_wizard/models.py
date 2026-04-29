from django.db import models
from .validators import validate_no_script_tags


# Policy Templates — admin-managed templates that instructors select from when
# creating a course policy. Editing a template does NOT update already-published
# policies (Policies table); publishing copies the body at that point in time.
class PolicyTemplates(models.Model):
    name = models.CharField(max_length=255)
    # Stores Quill Delta JSON (new) or plain text/HTML (legacy).
    # Replaced tinymce.models.HTMLField — both map to PostgreSQL TEXT.
    # The previous version had a duplicate field definition that silently
    # overrode HTMLField with TextField; this is now a single clean declaration.
    body = models.TextField(validators=[validate_no_script_tags])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


# Published Policies — one active policy per course, created when an instructor
# selects a template and clicks Publish. The body is a snapshot copied from the
# template at publish time.
class Policies(models.Model):
    course_id = models.IntegerField(null=True)
    context_id = models.CharField(max_length=255, null=True)
    related_template = models.ForeignKey(PolicyTemplates, null=True, on_delete=models.CASCADE, related_name="related_policies")
    is_published = models.SmallIntegerField()
    published_by = models.CharField(max_length=255)
    is_active = models.SmallIntegerField()
    # Stores Quill Delta JSON (new) or HTML (legacy). Rendered to HTML at
    # display time via the |render_body template filter.
    # Replaced tinymce.models.HTMLField — both map to PostgreSQL TEXT.
    body = models.TextField(validators=[validate_no_script_tags])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
