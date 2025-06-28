from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'issues', views.IssueViewSet)
router.register(r'machines', views.MachineViewSet, basename='machine')
router.register(r'departments', views.DepartmentViewSet, basename='department')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dashboard/metrics/', views.dashboard_metrics, name='dashboard_metrics'),
    path('ai/improve-description/', views.improve_description, name='improve_description'),
    path('improve_remedy_description/', views.improve_remedy_description, name='improve_remedy_description'),
] 