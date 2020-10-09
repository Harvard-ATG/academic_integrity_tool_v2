from django.urls import path

from . import views

urlpatterns = [
    path('', views.process_lti_launch_request_view, name='process_lti_launch_request'),
    path('refresh', views.lti_exception_view, name='lti_exception_view'),
    path('policy_templates_list/', views.policy_templates_list_view, name='policy_templates_list'),
    path('student_active_policy/', views.student_active_policy_view, name='student_active_policy'),
    path('template/<int:pk>/edit/', views.admin_level_template_edit_view, name='admin_level_template_edit'),
    path('updated_template/<int:pk>/', views.admin_updated_template_view, name='admin_updated_template'),
    path('edit_updated_template/<int:pk>/edit/', views.admin_edit_updated_template_view, name='admin_edit_updated_template'),
    path('policy/<int:pk>/edit/', views.instructor_level_policy_edit_view, name='instructor_level_policy_edit'),
    path('active_policy/<int:pk>/', views.instructor_active_policy, name='instructor_active_policy'),
    path('edit_active_policy/<int:pk>/', views.edit_active_policy, name='edit_active_policy'),
    path('instructor_inactivate_policies/', views.instructor_inactivate_policies_view, name='instructor_inactivate_policies'),
]
