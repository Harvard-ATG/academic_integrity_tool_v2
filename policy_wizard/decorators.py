from django.core.exceptions import PermissionDenied

def require_role_administrator(some_function):

    def wrapper(request, pk):
        if request.session['role'] == 'Administrator':
            return some_function(request, pk)
        else:
            raise PermissionDenied
    
    return wrapper

def require_role_instructor(some_function):
    def wrapper(request, pk):
        if request.session['role'] == 'Instructor':
            return some_function(request, pk)
        else:
            raise PermissionDenied

    return wrapper

def require_role_student(some_function):
    def wrapper(request):
        if request.session['role'] == 'Student':
            return some_function(request)
        else:
            raise PermissionDenied

    return wrapper