from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PolicyTemplates(models.Model):
    name = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Policies(models.Model):
    context_id = models.CharField(max_length=255)
    related_template = models.ForeignKey(PolicyTemplates, null=True, on_delete=models.CASCADE, related_name="related_policies")
    is_published = models.BooleanField()
    published_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_policies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)