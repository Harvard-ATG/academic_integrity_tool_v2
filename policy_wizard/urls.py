from django.urls import path

from . import views

urlpatterns = [
    #path('administrator', views.admin_level_template_view, name='admin_level_template_list'),
    #path('instructor', views.instructor_level_template_view, name='policy_template_list'),

    path('student', views.student_published_policy_view, name='student_published_policy'),
    path('template/<int:pk>/edit', views.AdminLevelTemplateUpdateView.as_view(), name='admin_level_template_edit'),
    path('policy/<int:pk>/edit', views.instructor_level_policy_edit_view, name='instructor_level_policy_edit'),
    path('published_policy/<int:pk>/', views.instructor_published_policy, name='instructor_published_policy'),
    path('<str:role>', views.policy_templates_list_view, name='policy_templates_list'),
    path('edit_published_policy/<int:pk>/', views.edit_published_policy, name='edit_published_policy'),
]
