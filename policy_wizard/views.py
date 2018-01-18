from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy

from .models import PolicyTemplates, Policies

# Create your views here.
class PolicyTemplateListView(ListView):
    model = PolicyTemplates
    template_name = 'policy_template_list.html'
"""
class PolicyTemplateUpdateView(UpdateView):
    model = PolicyTemplates
    fields = ['name', 'body']
    template_name = 'policy_template_edit.html'
    success_url = reverse_lazy('policy_template_list')
"""

def policy_edit_view(request, pk):
    policy=PolicyTemplates.objects.get(pk=pk)
    return render(request, 'policy_edit.html', {'policy': policy})


"""
class PublishedPolicyView()
policy_template_id = models.IntegerField()
    is_published = models.BooleanField()
    published_by = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
"""


"""
def about_company(request):
    # do something else...
    # return some data along with the view...
    return render(request, 'about_company.html', {'company_name': 'Simple Complex'})
"""


