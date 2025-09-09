import logging

from pylti.common import LTIException

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from .models import PolicyTemplates, Policies
from .utils import role_identifier, validate_request, inactivate_active_policies
from .forms import PolicyTemplateForm, NewPolicyForm
from django.views.decorators.clickjacking import xframe_options_exempt
from .decorators import require_role_administrator, require_role_instructor, require_role_student
from . import roles
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
@xframe_options_exempt #Allows rendering in Canvas frame
def process_lti_launch_request_view(request):
    '''
    Processes launch request and redirects to appropriate view depending on the role of the launcher
    '''
        # --- TEMPORARY DEBUGGING ---
    print("--- LTI URL DEBUGGING ---")
    print(f"Request Scheme: {request.scheme}")
    print(f"Request Host: {request.get_host()}")
    print(f"Absolute URI Django is using: {request.build_absolute_uri()}")
    print("--------------------------")

    import pprint
    data = {
      'scheme': request.scheme,
      'is_secure': request.is_secure(),
      'host': request.get_host(),
      'X-Fwd-Proto': request.META.get('HTTP_X_FORWARDED_PROTO'),
      'headers': {k: v for k, v in request.META.items() if k.startswith('HTTP_')},
    }
    print('<pre>' + pprint.pformat(data) + '</pre>')
    # --- END DEBUGGING ---

    #True if this is a typical lti launch. False if not.
    is_basic_lti_launch = request.method == 'POST' and request.POST.get(
        'lti_message_type') == 'basic-lti-launch-request'

    try:
        request_is_valid = validate_request(request)
    except LTIException: # oauth session may have timed out or the keys may be wrong
        return redirect('lti_exception_view')

    if is_basic_lti_launch and request_is_valid: #if typical lti launch and request is valid ...

        #Store the context_id in the request's session attribute.
        #A 'context_id' is a unique opaque identifier for the context from which this wizard is launched.
        #Thus, if the wizard is launched from a canvas course site, the context_id will point to the canvas
        #course site.
        request.session['context_id'] = request.POST.get('context_id')

        # Store the custom_canvas_course_id in the request's session attribute.
        # A custom_canvas_course_id is a unique identifier for a canvas course site.
        # You can find the Canvas course associated with it more easily than you can with a course's context_id.
        request.session['course_id'] = request.POST.get('custom_canvas_course_id')

        #Figure out role of launcher and store the role in the request's session attribute
        request.session['role'] = role_identifier(request.POST.get('ext_roles'))

        #Store the 'lis_person_sourcedid', a unique identifier of the launcher, in the request's session attribute.
        #This is used later to indicate the author of a course policy.
        request.session['lis_person_sourcedid'] = request.POST.get('lis_person_sourcedid')

        #Using the role, e.g. 'Administrator', 'Instructor', or 'Student', determine route to take
        role = request.session.get('role')
        if role==roles.ADMINISTRATOR or role==roles.INSTRUCTOR:
            test_result = cache.get('my_test_key')
            print("test_result_from_cache_process_lti_method", test_result)
            return redirect('policy_templates_list')
        elif role==roles.STUDENT:
            return redirect('student_active_policy')
    else: #if not typical lti launch or if request is not valid ...
        raise PermissionDenied

@xframe_options_exempt
def lti_exception_view(request):
    return render(request, 'lti_exception.html', {})

@xframe_options_exempt
def policy_templates_list_view(request):
    '''
    Displays list of policy templates
    '''

    test_result = cache.get('my_test_key')
    print("test_result_from_cache_policy_templates_list_view_method", test_result)
    
    #Fetch role from session attribute. It should be either 'Administrator' or 'Instructor'.
    role = request.session.get('role')

    if role==roles.INSTRUCTOR or role==roles.ADMINISTRATOR:

        if role==roles.INSTRUCTOR:
            try: #If there is an active policy for this course, get it. (Only 1 active policy expected.)
                active_policy = Policies.objects.get(course_id=request.session['course_id'], is_active=True)
                # Render the active policy
                return render(request, 'instructor_active_policy.html', {'active_policy': active_policy})
            except Policies.MultipleObjectsReturned: #If multiple active policies exist (which should never happen)...
                # ... return the latest active policy
                active_policy = Policies.objects.filter(course_id=request.session['course_id'], is_active=True).latest('created_at')
                return render(request, 'instructor_active_policy.html', {'active_policy': active_policy})
            except Policies.DoesNotExist: #If no active policy exists ...
                pass


        #Fetch each policy template from the `PolicyTemplates` table in the database and store as a variable
        maximally_restrictive_policy_template = PolicyTemplates.objects.get(name="Maximally Restrictive Policy")
        mixed_policy_template = PolicyTemplates.objects.get(name="Mixed Policy")
        fully_encouraging_policy_template = PolicyTemplates.objects.get(name="Fully-Encouraging Policy")
        # written_work_policy_template = PolicyTemplates.objects.get(name="Collaboration Permitted: Written Work")
        # problem_sets_policy_template = PolicyTemplates.objects.get(name="Collaboration Permitted: Problem Sets")
        # collaboration_prohibited_policy_template = PolicyTemplates.objects.get(name="Collaboration Prohibited")
        custom_policy_template = PolicyTemplates.objects.get(name="Custom Policy")

        if role==roles.ADMINISTRATOR:
            #Django template to use
            template_to_use = 'admin_level_template_list.html'
            list_level = 'admin_level_template_edit'
            button_text = 'Update'
        else: #role=='Instructor'
            # Django template to use
            template_to_use = 'instructor_level_template_list.html'
            list_level = 'instructor_level_policy_edit'
            button_text = 'Choose'

        #Render the policy templates
        return render(
            request,
            template_to_use,
            {
                # 'written_work_policy_template': written_work_policy_template,
                # 'problem_sets_policy_template': problem_sets_policy_template,
                # 'collaboration_prohibited_policy_template': collaboration_prohibited_policy_template,
                'maximally_restrictive_policy_template': maximally_restrictive_policy_template,
                'mixed_policy_template': mixed_policy_template,
                'fully_encouraging_policy_template': fully_encouraging_policy_template,
                'custom_policy_template': custom_policy_template,
                'list_level': list_level,
                'button_text': button_text
            })

    else: #i.e. 'Student'
        raise PermissionDenied


@xframe_options_exempt
@require_role_administrator
def admin_level_template_edit_view(request, pk):
    '''
    Presents the text editor to an administrator so they can edit and update a policy template
    '''
    template_to_update = get_object_or_404(PolicyTemplates, pk=pk)

    if request.method == 'POST':
        form = PolicyTemplateForm(request.POST)
        if form.is_valid():
            template_to_update.body = form.cleaned_data.get('body')
            template_to_update.save()
            return redirect('admin_updated_template', pk=template_to_update.pk)
    else:
        form = PolicyTemplateForm(initial={'body': template_to_update.body})
    return render(request, 'admin_level_template_edit.html', {'form': form, 'template_to_update': template_to_update})

@xframe_options_exempt
@require_role_administrator
def admin_updated_template_view(request, pk):
    '''
    Present the updated template to the administrator
    '''
    updated_template = PolicyTemplates.objects.get(pk=pk)
    return render(request, 'admin_updated_template.html', {'updated_template': updated_template})

@xframe_options_exempt
@require_role_administrator
def admin_edit_updated_template_view(request, pk):
    '''
    Present administrator with editor so they can edit a template they just updated
    '''
    template_to_update = get_object_or_404(PolicyTemplates, pk=pk)

    if request.method == 'POST':
        form = PolicyTemplateForm(request.POST)
        if form.is_valid():
            template_to_update.body = form.cleaned_data.get('body')
            template_to_update.save()
            return redirect('admin_updated_template', pk=template_to_update.pk)
    else:
        form = PolicyTemplateForm(initial={'body': template_to_update.body})
    return render(request, 'admin_edit_updated_template.html', {'form': form, 'template_to_update': template_to_update})

@xframe_options_exempt
@require_role_instructor
def instructor_level_policy_edit_view(request, pk):
    '''
    Presents the text editor to an instructor so they can edit and publish a policy
    '''

    policy_template = get_object_or_404(PolicyTemplates, pk=pk)

    if request.method == 'POST':
        form = NewPolicyForm(request.POST)
        if form.is_valid():
            # First, inactivate any active policies for the course that may be present in the database ...
            # (Ensures there is ever only one active policy for the course)
            inactivate_active_policies(request)
            # ... then create a new active policy for the course
            finalPolicy = Policies.objects.create(
                course_id=request.session['course_id'],
                context_id=request.session['context_id'],
                body=form.cleaned_data.get('body'),
                related_template = policy_template,
                published_by = request.session['lis_person_sourcedid'],
                is_published = True,
                is_active=True,
            )

            return redirect('instructor_active_policy', pk=finalPolicy.pk)
    else:
        form = NewPolicyForm(initial={'body': policy_template.body})
    return render(request, 'instructor_level_policy_edit.html', {'policy_template': policy_template, 'form': form})

@xframe_options_exempt
@require_role_instructor
def instructor_active_policy(request, pk):
    '''
    Displays to the instructor the policy they just prepared
    '''
    active_policy = Policies.objects.get(pk=pk)
    return render(request, 'instructor_active_policy.html', {'active_policy': active_policy})

@xframe_options_exempt
@require_role_instructor
def edit_active_policy(request, pk):
    '''
    Provides an instructor the capability to edit a policy they already published
    '''
    policy_to_edit = Policies.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewPolicyForm(request.POST)
        if form.is_valid():
            # First, inactivate any active policies for the course that may be present in the database ...
            # (Ensures there is ever only one active policy for the course)
            inactivate_active_policies(request)
            # ... then mark the edited policy as active, and save
            policy_to_edit.body = form.cleaned_data.get('body')
            policy_to_edit.is_active=True
            policy_to_edit.save()
            return redirect('instructor_active_policy', pk=policy_to_edit.pk)
    else:
        form = NewPolicyForm(initial={'body': policy_to_edit.body})
    return render(request, 'instructor_level_policy_edit.html', {'policy_template': policy_to_edit, 'form': form})

@xframe_options_exempt
@require_role_instructor
def instructor_inactivate_policies_view(request):
    '''
    Enables an instructor to inactivate an already published policy (including any other active policies that may
    be present) and redirects to the list of policy templates
    '''
    inactivate_active_policies(request)
    # Redirect to list of templates
    return redirect('policy_templates_list')

@xframe_options_exempt
@require_role_student
def student_active_policy_view(request):
    '''
    Displays to the student the policy for the course if one exists
    '''
    try:
        # If an active policy exists (Only 1 expected)...
        active_policy = Policies.objects.get(course_id=request.session['course_id'], is_active=True)
        # Render the policy
        return render(request, 'student_active_policy.html', {'active_policy': active_policy})
    except Policies.DoesNotExist: #If no active policy exists ...
        return render(request, 'student_missing_policy.html')
    except Policies.MultipleObjectsReturned: #If multiple active policies present (which should never happen) ...
        # ... return the latest active policy
        active_policy = Policies.objects.filter(course_id=request.session['course_id'], is_active=True).latest('created_at')
        return render(request, 'instructor_active_policy.html', {'active_policy': active_policy})
