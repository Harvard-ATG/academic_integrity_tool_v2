from functools import wraps
from django.core.exceptions import PermissionDenied
from . import roles

def require_role(permitted_role):
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            given_role = request.session.get('role')
            if given_role == permitted_role:
                return view_function(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator

require_role_administrator = require_role(roles.ADMINISTRATOR)
require_role_instructor = require_role(roles.INSTRUCTOR)
require_role_student = require_role(roles.STUDENT)
