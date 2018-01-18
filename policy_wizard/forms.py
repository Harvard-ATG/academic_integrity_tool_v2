from django import forms
from .models import PolicyTemplates

class NewPolicyForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(), max_length=4000)

    class Meta:
        model = PolicyTemplates
        fields = ['name', 'body']