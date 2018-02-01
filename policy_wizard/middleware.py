from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
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
    # E.g., from [urn:lti:role:ims/lis/Student, urn:lti:sysrole:ims/lis/User]
    # obtain 'urn:lti:role:ims/lis/Student'
    relevant_role_component = ext_roles_text_as_list[-2]
    # E.g., transform 'urn:lti:role:ims/lis/Student' to [urn:lti:role:ims, lis, Student]
    relevant_role_component_as_list = relevant_role_component.split("/")
    # E.g., from [urn:lti:role:ims, lis, Student], obtain 'Student'
    actual_role = relevant_role_component_as_list[-1]

    # E.g., 'Student', or 'Instructor', or 'Administrator', e.t.c.
    return actual_role


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