from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views
from django.contrib.auth import views as auth_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'issues', views.IssueViewSet)
router.register(r'machines', views.MachineViewSet, basename='machine')
router.register(r'departments', views.DepartmentViewSet, basename='department')

# RBAC Management Routes
router.register(r'roles', admin_views.RoleViewSet, basename='role')
router.register(r'permissions', admin_views.PermissionViewSet, basename='permission')
router.register(r'user-roles', admin_views.UserRoleViewSet, basename='user-role')
router.register(r'public-role', admin_views.PublicRoleViewSet, basename='public-role')
router.register(r'global-settings', admin_views.GlobalSettingsViewSet, basename='global-settings')

urlpatterns = [
    # Authentication endpoints (before router to avoid conflicts)
    path('auth/login/', views.LoginView.as_view(), name='api-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('auth/user/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/csrf/', views.CSRFTokenView.as_view(), name='csrf-token'),
    
    # Custom endpoints (before router to avoid conflicts)
    path('issues/<uuid:issue_id>/generate_report/', views.generate_report_view, name='generate_report'),
    path('dashboard/metrics/', views.dashboard_metrics, name='dashboard_metrics'),
    path('ai/improve-description/', views.improve_description, name='improve_description'),
    path('improve_remedy_description/', views.improve_remedy_description, name='improve_remedy_description'),
    
    # Remedy endpoints
    path('issues/<uuid:issue_pk>/remedies/', views.RemedyViewSet.as_view({'get': 'list', 'post': 'create'}), name='issue-remedies-list'),
    path('issues/<uuid:issue_pk>/remedies/<uuid:pk>/', views.RemedyViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='issue-remedies-detail'),
    path('issues/<uuid:issue_pk>/remedies/<uuid:pk>/attachments/', views.RemedyViewSet.as_view({'post': 'add_attachment'}), name='issue-remedies-attachments'),
    path('issues/<uuid:issue_pk>/remedies/<uuid:pk>/attachments/<uuid:attachment_id>/', views.RemedyViewSet.as_view({'delete': 'delete_attachment'}), name='issue-remedies-attachment-delete'),
    
    # Issue attachment endpoints
    path('issues/<uuid:pk>/attachments/<uuid:attachment_id>/', views.IssueViewSet.as_view({'delete': 'delete_attachment'}), name='issue-attachment-delete'),
    
    # ViewSet routes (last to avoid conflicts)
    path('', include(router.urls)),
]