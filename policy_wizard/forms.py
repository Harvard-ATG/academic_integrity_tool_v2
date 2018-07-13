from django.forms import ModelForm, Textarea
from .models import PolicyTemplates, Policies
from django.utils.translation import gettext_lazy as _

class NewPolicyForm(ModelForm):

    class Meta:
        model = Policies
        fields = ['body']
        labels = {
            'body': _(''),
        }
        widgets = {
            'body': Textarea(attrs={'cols': 80, 'rows': 1000}),
        }

class PolicyTemplateForm(ModelForm):
    class Meta:
        model = PolicyTemplates
        fields = ['body']
        labels = {
            'body': _(''),
        }
        widgets = {
            'body': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
