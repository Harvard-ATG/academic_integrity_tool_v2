from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from .forms import NewPolicyForm
from lti_provider.lti import LTI

from django.conf import settings
from .models import PolicyTemplates, Policies
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def determine_role_view(request):
    # validate LTI request
    def validate_request(request):
        consumer_key = settings.SECURE_SETTINGS['CONSUMER_KEY']
        shared_secret = settings.SECURE_SETTINGS['LTI_SECRET']

        if consumer_key is None or shared_secret is None:
            raise ImproperlyConfigured("Unable to validate LTI launch. Missing setting: CONSUMER_KEY or LTI_SECRET")

        #Instantiate an LTI object with an 'initial' request type and 'any' role type
        lti_object = LTI('initial', 'any')

        #return True if request is valid or False if otherwise
        return lti_object._verify_request(request)

    is_basic_lti_launch = request.method=='POST' and request.POST.get('lti_message_type')=='basic-lti-launch-request'

    request_is_valid = validate_request(request)


    if is_basic_lti_launch and request_is_valid:
        if request.POST.get('roles')=='Instructor':
            return redirect('policy_template_list')
        elif request.POST.get('roles')=='Student':
            return redirect('published_policy_to_display')
        elif request.POST.get('roles')=='Technologist':
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




