from django import forms
from .models import Policies

class NewPolicyForm(forms.ModelForm):
    class Meta:
        model = Policies
        fields = ['body']