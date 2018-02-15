from django import forms
from .models import Policies
from tinymce.widgets import TinyMCE

class NewPolicyForm(forms.ModelForm):

    class Meta:
        model = Policies
        fields = ['body']