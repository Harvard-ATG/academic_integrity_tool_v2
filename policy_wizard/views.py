from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import NewPolicyForm

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
    policyTemplate = get_object_or_404(PolicyTemplates, pk=pk)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewPolicyForm(request.POST)
        if form.is_valid():
            #form.save()
            #editedPolicy = form.save(commit=False)
            #editedPolicy.is_published = True
            #editedPolicy.published_by = user
            #editedPolicy.related_template = policyTemplate
            #editedPolicy.save()
            Policies.objects.create(
                body=form.cleaned_data.get('body'),
                related_template = policyTemplate,
                published_by = user,
                is_published = True,
            )
            return redirect('policy_template_list')
    else:
        form = NewPolicyForm(initial={'body': policyTemplate.body})
    return render(request, 'policy_edit.html', {'policyTemplate': policyTemplate, 'form': form})


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


