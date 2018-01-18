from django.urls import path

from . import views

urlpatterns = [
    #path('technologist', views.PolicyTemplateListView.as_view(), name='policy_template_list'),
    path('instructor', views.PolicyTemplateListView.as_view(), name='policy_template_list'),
    #path('template/<int:pk>/edit', views.PolicyTemplateUpdateView.as_view(), name='policy_template_edit'),
    path('policy/<int:pk>/edit', views.policy_edit_view, name='policy_edit'),
    path('published_policy/<int:pk>/', views.published_policy, name='published_policy'),
]

"""
def url(regex, view, kwargs=None, name=None):
    # ...
    
Arbitrary keyword arguments that’s passed to the target view. It is normally used to do some simple customization on reusable views
"""