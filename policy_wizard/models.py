from django.db import models

# Create your models here.
class PolicyTemplates(models.Model):
    name = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

class Policies(models.Model):
    policy_template_id = models.IntegerField()
    is_published = models.BooleanField()
    published_by = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()