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


    def role_identifier(ext_roles_text):
        """
        :param ext_roles_text: This will be the value of the 'ext_roles' attribute in the POST request lti forms.
        It is a string, like 'urn:lti:role:ims/lis/Student,urn:lti:sysrole:ims/lis/User'
        :return: A one word string, namely, the actual role. E.g. 'Student'
        """

        #E.g., transform 'urn:lti:role:ims/lis/Student,urn:lti:sysrole:ims/lis/User'
        # to [urn:lti:role:ims/lis/Student, urn:lti:sysrole:ims/lis/User]
        ext_roles_text_as_list = ext_roles_text.split(",")
        #E.g., from [urn:lti:role:ims/lis/Student, urn:lti:sysrole:ims/lis/User]
        # obtain 'urn:lti:role:ims/lis/Student'
        relevant_role_component = ext_roles_text_as_list[-2]
        #E.g., transform 'urn:lti:role:ims/lis/Student' to [urn:lti:role:ims, lis, Student]
        relevant_role_component_as_list = relevant_role_component.split("/")
        #E.g., from [urn:lti:role:ims, lis, Student], obtain 'Student'
        actual_role = relevant_role_component_as_list[-1]

        #E.g., 'Student', or 'Instructor', or 'Administrator', e.t.c.
        return actual_role

    # validates LTI request
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




