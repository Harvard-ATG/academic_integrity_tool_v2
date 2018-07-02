from functools import wraps
from django.core.exceptions import PermissionDenied

def require_role_administrator(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'Administrator':
            return view_function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    return wrapper

def require_role_instructor(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'Instructor':
            return view_function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper

def require_role_student(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'Student':
            return view_function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper