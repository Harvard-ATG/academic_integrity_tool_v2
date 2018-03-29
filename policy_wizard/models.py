from django.db import models
from django.contrib.auth.models import User
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
    context_id = models.CharField(max_length=255, blank=False)
    related_template = models.ForeignKey(PolicyTemplates, null=True, on_delete=models.CASCADE, related_name="related_policies")
    is_published = models.BooleanField()
    published_by = models.CharField(max_length=255)
    body = tinymce_models.HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

