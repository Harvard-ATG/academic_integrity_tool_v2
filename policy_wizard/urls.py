from django.urls import path

from . import views

urlpatterns = [
    path('technologist', views.admin_level_template_view, name='admin_level_template_list'),
    path('instructor', views.PolicyTemplateListView.as_view(), name='policy_template_list'),
    path('template/<int:pk>/edit', views.PolicyTemplateUpdateView.as_view(), name='policy_template_edit'),
    path('policy/<int:pk>/edit', views.policy_edit_view, name='policy_edit'),
    path('published_policy/<int:pk>/', views.published_policy, name='published_policy'),
]
