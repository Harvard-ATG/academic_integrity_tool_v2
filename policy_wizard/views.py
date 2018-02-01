from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import NewPolicyForm
from .models import PolicyTemplates, Policies
from .middleware import role_identifier, validate_request


# Create your views here.
@csrf_exempt
def determine_role_view(request):

    is_basic_lti_launch = request.method=='POST' and request.POST.get('lti_message_type')=='basic-lti-launch-request'

    request_is_valid = validate_request(request)

    role = role_identifier(request.POST.get('ext_roles'))

    if is_basic_lti_launch and request_is_valid:
        if role=='Instructor' or role=='Mentor':
            return redirect('policy_template_list')
        elif role=='Student':
            return redirect('published_policy_to_display')
        elif role=='Technologist' or role=='Administrator':
            return redirect('admin_level_template_list')
    else:
        raise PermissionDenied


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

    #Arbitrary user selection
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

def published_policy_to_display_view(request):

    """
    Code that determines the published policy to display based on course
    student is taking ...
    """

    # Arbitrary policy selection
    publishedPolicy = Policies.objects.first()

    return render(request, 'published_policy.html', {'publishedPolicy': publishedPolicy})




