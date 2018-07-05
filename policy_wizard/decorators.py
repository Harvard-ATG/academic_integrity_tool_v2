from functools import wraps
from django.core.exceptions import PermissionDenied
from .roles import ROLES

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

require_role_admin = require_role(ROLES.get("ADMIN"))
require_role_instructor = require_role(ROLES.get("INSTRUCTOR"))
require_role_student = require_role(ROLES.get("STUDENT"))
