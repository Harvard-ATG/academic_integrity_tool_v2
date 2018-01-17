from django.contrib import admin
from .models import PolicyTemplates, Policies

# Register your models here.
admin.site.register(PolicyTemplates)
admin.site.register(Policies)
