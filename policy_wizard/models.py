from django.db import models
from tinymce import models as tinymce_models

# Create your models here.

#Policy Templates
class PolicyTemplates(models.Model):
    name = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

#Published policies
class Policies(models.Model):
    course_id = models.IntegerField(null=True)
    context_id = models.CharField(max_length=255, null=True)
    related_template = models.ForeignKey(PolicyTemplates, null=True, on_delete=models.CASCADE, related_name="related_policies")
    is_published = models.SmallIntegerField()
    published_by = models.CharField(max_length=255)
    is_active = models.SmallIntegerField()
    body = tinymce_models.HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

