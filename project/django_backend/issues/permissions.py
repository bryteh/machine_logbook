from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from .models import PublicRole


class HasPermission(BasePermission):
    """Flexible permission class that checks both authenticated and public users"""
    permission_required = None
    
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            # Check public permissions
            try:
                public_role = PublicRole.load()
                return public_role.has_permission(self.permission_required)
            except:
                return False
        
        # Check authenticated user permissions
        if not hasattr(request.user, 'role') or not request.user.role:
            return False
        
        return request.user.role.has_permission(self.permission_required)


class CanViewDashboard(HasPermission):
    permission_required = 'view_dashboard'


class CanCRUDIssues(HasPermission):
    permission_required = 'crud_issues'


class CanCRUDRemedies(HasPermission):
    permission_required = 'crud_remedies'


class CanMarkResolved(HasPermission):
    permission_required = 'mark_resolved'


class CanConfigureLimits(HasPermission):
    permission_required = 'configure_limits'


class CanManageUsers(HasPermission):
    permission_required = 'manage_users'


class CanViewCosts(HasPermission):
    permission_required = 'view_costs'


class CanViewExternalContacts(HasPermission):
    permission_required = 'view_external_contacts'


class CanGenerateReports(HasPermission):
    permission_required = 'generate_reports'


class IsPublicOrAuthenticated(BasePermission):
    """Allow public users for specific actions, authenticated users for all"""
    
    def has_permission(self, request, view):
        # Always allow GET requests (reading data)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # For POST (create), check if public users are allowed
        if request.method == 'POST':
            if isinstance(request.user, AnonymousUser):
                try:
                    public_role = PublicRole.load()
                    # Check if public users can create for this specific view
                    view_name = view.__class__.__name__.lower()
                    if 'issue' in view_name:
                        return public_role.has_permission('crud_issues')
                    elif 'remedy' in view_name:
                        return public_role.has_permission('crud_remedies')
                    
                    # Also check by model if available
                    if hasattr(view, 'model'):
                        model_name = view.model.__name__.lower()
                        if model_name == 'issue':
                            return public_role.has_permission('crud_issues')
                        elif model_name == 'remedy':
                            return public_role.has_permission('crud_remedies')
                    
                    # Also check queryset model
                    if hasattr(view, 'queryset') and view.queryset is not None:
                        model_name = view.queryset.model.__name__.lower()
                        if model_name == 'issue':
                            return public_role.has_permission('crud_issues')
                        elif model_name == 'remedy':
                            return public_role.has_permission('crud_remedies')
                    
                    return False
                except:
                    return False
        
        # For other methods (PUT, PATCH, DELETE), require authentication
        return not isinstance(request.user, AnonymousUser)


class DynamicPermission(BasePermission):
    """Dynamic permission class that can be configured at runtime"""
    
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename
    
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            try:
                public_role = PublicRole.load()
                return public_role.has_permission(self.permission_codename)
            except:
                return False
        
        if not hasattr(request.user, 'role') or not request.user.role:
            return False
        
        return request.user.role.has_permission(self.permission_codename) 