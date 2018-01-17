from django.urls import path

from . import views

urlpatterns = [
    path('technologist', views.PolicyTemplateListView.as_view(), name='policy_template_list'),
    path('instructor', views.PolicyTemplateListView.as_view(), name='policy_template_list'),
    path('template/<int:pk>/edit', views.PolicyTemplateUpdateView.as_view(), name='policy_template_edit'),
]