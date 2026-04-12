"""
Dev-only view that simulates an LTI launch by seeding the session with
a chosen role.  Gated by settings.DEBUG so it can never run in production.

Usage:
    http://localhost:8000/dev/login/instructor/
    http://localhost:8000/dev/login/student/
    http://localhost:8000/dev/login/admin/
"""
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect

from policy_wizard import roles

# Map URL slugs to the role constants the app expects.
ROLE_MAP = {
    'instructor': roles.INSTRUCTOR,
    'student': roles.STUDENT,
    'admin': roles.ADMINISTRATOR,
}

# Fake values that satisfy the session keys views depend on.
DEV_COURSE_ID = 99999
DEV_CONTEXT_ID = 'dev-context-1'
DEV_PERSON_ID = 'dev-user'


def dev_login_view(request, role_slug):
    """Seed the session and redirect to the appropriate landing page."""
    if not settings.DEBUG:
        raise Http404

    role = ROLE_MAP.get(role_slug)
    if role is None:
        return HttpResponse(
            f"Unknown role '{role_slug}'. Use one of: {', '.join(ROLE_MAP.keys())}",
            status=400,
        )

    request.session['role'] = role
    request.session['course_id'] = DEV_COURSE_ID
    request.session['context_id'] = DEV_CONTEXT_ID
    request.session['lis_person_sourcedid'] = DEV_PERSON_ID

    if role == roles.STUDENT:
        return redirect('student_active_policy')
    else:
        return redirect('policy_templates_list')
