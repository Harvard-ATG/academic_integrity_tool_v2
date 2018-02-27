from django import forms
from .models import Policies
from tinymce.widgets import TinyMCE
from django.forms import ModelForm, Textarea
from .models import PolicyTemplates, Policies

class NewPolicyForm(ModelForm):

    class Meta:
        model = Policies
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={'cols': 80, 'rows': 1000}),
        }

class PolicyTemplateForm(ModelForm):
    class Meta:
        model = PolicyTemplates
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
