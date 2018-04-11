from django.core.exceptions import PermissionDenied

def require_role_admin(some_function):

    def wrapper(request, pk):
        if request.session['role'] == 'Administrator':
            return some_function(request, pk)
        else:
            raise PermissionDenied
    
    return wrapper