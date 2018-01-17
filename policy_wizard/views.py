from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import PolicyTemplates

# Create your views here.
class PolicyTemplateListView(ListView):
    model = PolicyTemplates
    template_name = 'policy_template_list.html'

class PolicyTemplateUpdateView(UpdateView):
    model = PolicyTemplates
    fields = ['name', 'body']
    template_name = 'policy_template_edit.html'
    success_url = reverse_lazy('policy_template_list')

