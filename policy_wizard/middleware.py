from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from lti_provider.lti import LTI

def role_identifier(ext_roles_text):
    """
    :param ext_roles_text: This will be the value of the 'ext_roles' attribute in the POST request lti forms.
    It is a string, like 'urn:lti:role:ims/lis/Student,urn:lti:sysrole:ims/lis/User'
    :return: A one word string, namely, the actual role. E.g. 'Student'
    """

    # E.g., transform 'urn:lti:role:ims/lis/Student,urn:lti:sysrole:ims/lis/User'
    # to [urn:lti:role:ims/lis/Student, urn:lti:sysrole:ims/lis/User]
    ext_roles_text_as_list = ext_roles_text.split(",")

    # Store the context roles in context_roles and the non-context roles (institution and system roles) in non_context_roles
    # For context/institution/system role reference, see https://www.imsglobal.org/specs/ltiv1p1/implementation-guide#toc-29
    context_roles = []
    non_context_roles = []
    for role in ext_roles_text_as_list:
        if 'lti:role' in role:
            context_roles.append(role)
        else:
            non_context_roles.append(role)

    #Determine the 'policy_role', i.e. the role to use in this app, by mapping from context/non_context roles
    # to the 3 role types (Administrator, Instructor, and Student) in this policy wizard
    if not bool(context_roles):#if context_roles list is empty, i.e. if there are no context roles...
        # Process the institutional and system roles
        for non_context_role in non_context_roles:
            if ('Administrator' or 'ContentDeveloper') in non_context_role:
                policy_role = 'Administrator'
                break
            else:
                raise PermissionDenied
    else: #if context_roles list is not empty
        context_roles_as_string = ''.join(context_roles) #convert context_roles to string
        if ('Administrator' in context_roles_as_string) or ('ContentDeveloper' in context_roles_as_string):
            policy_role = 'Administrator'
        elif ('Instructor' in context_roles_as_string):
            policy_role = 'Instructor'
        elif ('Learner' in context_roles_as_string) or ('NonCreditLearner' in context_roles_as_string) or ('TeachingAssistant' in context_roles_as_string) or ('Mentor' in context_roles_as_string):
            policy_role = 'Student'
        else:
            raise PermissionDenied

    return policy_role


# validates LTI request
def validate_request(request):
    consumer_key = settings.SECURE_SETTINGS['CONSUMER_KEY']
    shared_secret = settings.SECURE_SETTINGS['LTI_SECRET']

    if consumer_key is None or shared_secret is None:
        raise ImproperlyConfigured("Unable to validate LTI launch. Missing setting: CONSUMER_KEY or LTI_SECRET")

    # Instantiate an LTI object with an 'initial' request type and 'any' role type
    lti_object = LTI('initial', 'any')

    # return True if request is valid or False if otherwise
    return lti_object._verify_request(request)



