from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from lti_provider.lti import LTI, LTIException
from .models import Policies

def role_identifier(ext_roles_text):
    """
    :param ext_roles_text: This will be the value of the 'ext_roles' attribute in the POST request lti forms.
    It is a string, like 'urn:lti:instrole:ims/lis/Administrator,urn:lti:instrole:ims/lis/Instructor,
    urn:lti:instrole:ims/lis/Student,urn:lti:role:ims/lis/Instructor,urn:lti:sysrole:ims/lis/User'
    :return: A one word string, namely, the actual role. E.g. 'Student'
    """

    # E.g., transform 'urn:lti:instrole:ims/lis/Administrator,urn:lti:instrole:ims/lis/Instructor,
    # urn:lti:instrole:ims/lis/Student,urn:lti:role:ims/lis/Instructor,urn:lti:sysrole:ims/lis/User'
    # to [urn:lti:instrole:ims/lis/Administrator, urn:lti:instrole:ims/lis/Instructor,
    # urn:lti:instrole:ims/lis/Student, urn:lti:role:ims/lis/Instructor, urn:lti:sysrole:ims/lis/User]
    ext_roles_text_as_list = ext_roles_text.split(",")

    # Store the context roles in context_roles and the institutional roles in institutional_roles. Ignore system roles.
    # In this app, the institutional roles are used only when there are no context roles.
    # For context/institution/system role reference, see https://www.imsglobal.org/specs/ltiv1p1/implementation-guide#toc-29
    context_roles = []
    institutional_roles = []
    for role in ext_roles_text_as_list:
        if 'lti:role' in role:
            context_roles.append(role)
        elif 'lti:instrole' in role:
            institutional_roles.append(role)
        else:
            pass
    # Determine the 'policy_role', i.e. the role to use in this app, by mapping from context/institutional roles in Canvas
    # to the 3 role types (Administrator, Instructor, and Student) in this policy wizard app
    if bool(context_roles): #if context_roles list is not empty... (It is expected that if the launcher is registered in the course,
    # a context role will be present to reflect the launcher's role in the course.)
        context_roles_as_string = ''.join(context_roles)  # convert context_roles to string
        if ('Administrator' in context_roles_as_string):
            policy_role = 'Administrator'
        elif ('Instructor' in context_roles_as_string) or ('TeachingAssistant' in context_roles_as_string):
            policy_role = 'Instructor'
        else:
            policy_role = 'Student'
    else: #if context_roles list is empty... (This can happen in at least 2 cases: 1, when the canvas course site from which the wizard
    # is launched is current but the launcher is not registered in the course site, or 2, when the canvas course site from which the
    # wizard is launched is no longer current.)
        institutional_roles_as_string = ''.join(institutional_roles)  # convert institutional_roles to string
        if ('Administrator' in institutional_roles_as_string):
            policy_role = 'Administrator'
        else:
            policy_role = 'Student'

    return policy_role

# validates LTI request
def validate_request(request):

    consumer_key = settings.SECURE_SETTINGS['CONSUMER_KEY']
    shared_secret = settings.SECURE_SETTINGS['LTI_SECRET']

    if consumer_key is None or shared_secret is None:
        raise ImproperlyConfigured("Unable to validate LTI launch. Missing setting: CONSUMER_KEY or LTI_SECRET")

    # Instantiate an LTI object with an 'initial' request type and 'any' role type
    lti_object = LTI('initial', 'any')

    return lti_object._verify_request(request)

# Inactivates active policies for a particular course
def inactivate_active_policies(request):
    policies_to_inactivate = Policies.objects.filter(course_id=request.session['course_id'], is_active=True)
    policies_to_inactivate.update(is_active=False)