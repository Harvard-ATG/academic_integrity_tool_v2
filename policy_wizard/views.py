from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import NewPolicyForm

from .models import PolicyTemplates, Policies

# Create your views here.
def admin_level_template_view(request):
    templates = PolicyTemplates.objects.all()
    return render(request, 'admin_level_template_list.html', {'templates': templates})

class PolicyTemplateListView(ListView):
    model = PolicyTemplates
    template_name = 'policy_template_list.html'

class PolicyTemplateUpdateView(UpdateView):
    model = PolicyTemplates
    fields = ['name', 'body']
    template_name = 'policy_template_edit.html'
    success_url = reverse_lazy('admin_level_template_list')

def policy_edit_view(request, pk):
    policyTemplate = get_object_or_404(PolicyTemplates, pk=pk)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewPolicyForm(request.POST)
        if form.is_valid():
            finalPolicy = Policies.objects.create(
                body=form.cleaned_data.get('body'),
                related_template = policyTemplate,
                published_by = user,
                is_published = True,
            )

            return redirect('published_policy', pk=finalPolicy.pk)
    else:
        form = NewPolicyForm(initial={'body': policyTemplate.body})
    return render(request, 'policy_edit.html', {'policyTemplate': policyTemplate, 'form': form})

def published_policy(request, pk):
    publishedPolicy = Policies.objects.get(pk=pk)
    return render(request, 'published_policy.html', {'publishedPolicy': publishedPolicy})



