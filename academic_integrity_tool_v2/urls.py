"""academic_integrity_tool_v2 URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from lti_provider import views as lti_views
from .health_check_view import health_check_view


# Canvas GETs /lti/config during "By URL" tool installation, but other LMS
# implementations may POST.  Adding csrf_exempt + POST support ensures the
# XML config endpoint works regardless of HTTP method.
class LTIConfigViewWithPost(lti_views.LTIConfigView):
    """Extend LTIConfigView to accept POST (some LMS send POST during 'By URL' install)."""
    post = lti_views.LTIConfigView.get


urlpatterns = [
    path('health', health_check_view, name='health_check'),
    path('admin/', admin.site.urls),
    path('lti/launch/', include('policy_wizard.urls')),
    path('lti/config', csrf_exempt(LTIConfigViewWithPost.as_view()), name="get_lti_xml"),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    from policy_wizard.dev_views import dev_login_view
    urlpatterns += [
        path('dev/login/<str:role_slug>/', dev_login_view, name='dev_login'),
    ]


if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
