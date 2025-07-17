from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Role, Permission, UserRole, PublicRole, GlobalSettings
from .permissions import CanManageUsers, CanConfigureLimits
from .serializers import (
    RoleSerializer, PermissionSerializer, UserRoleSerializer, 
    PublicRoleSerializer, GlobalSettingsSerializer, UserSerializer
)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for permissions - used in role management UI"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [CanManageUsers]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get permissions grouped by category"""
        permissions = Permission.objects.all()
        categories = {}
        
        for perm in permissions:
            if perm.category not in categories:
                categories[perm.category] = []
            categories[perm.category].append({
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'description': perm.description
            })
        
        return Response(categories)


class RoleViewSet(viewsets.ModelViewSet):
    """Full CRUD for roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [CanManageUsers]
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a role with all its permissions"""
        original_role = self.get_object()
        
        new_name = request.data.get('name', f"{original_role.name} (Copy)")
        new_codename = request.data.get('codename', f"{original_role.codename}_copy")
        
        # Check if codename already exists
        if Role.objects.filter(codename=new_codename).exists():
            return Response(
                {'error': 'Role with this codename already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new role
        new_role = Role.objects.create(
            name=new_name,
            codename=new_codename,
            description=f"Cloned from {original_role.name}",
            is_active=True
        )
        
        # Copy permissions
        new_role.permissions.set(original_role.permissions.all())
        
        serializer = self.get_serializer(new_role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def permission_matrix(self, request):
        """Get a matrix view of all roles and their permissions"""
        roles = Role.objects.all()
        permissions = Permission.objects.all()
        
        matrix = []
        for role in roles:
            role_permissions = set(role.permissions.values_list('codename', flat=True))
            row = {
                'role': {
                    'id': role.id,
                    'name': role.name,
                    'codename': role.codename
                },
                'permissions': {}
            }
            
            for perm in permissions:
                row['permissions'][perm.codename] = perm.codename in role_permissions
            
            matrix.append(row)
        
        return Response({
            'matrix': matrix,
            'permissions': [{'codename': p.codename, 'name': p.name, 'category': p.category} for p in permissions]
        })


class UserRoleViewSet(viewsets.ModelViewSet):
    """Full CRUD for user role assignments"""
    queryset = UserRole.objects.select_related('user', 'role')
    serializer_class = UserRoleSerializer
    permission_classes = [CanManageUsers]
    
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """Get users without assigned roles"""
        assigned_user_ids = UserRole.objects.values_list('user_id', flat=True)
        available_users = User.objects.exclude(id__in=assigned_user_ids)
        
        serializer = UserSerializer(available_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_permission_override(self, request, pk=None):
        """Set individual permission override for a user"""
        user_role = self.get_object()
        permission_codename = request.data.get('permission')
        granted = request.data.get('granted', False)
        
        if not permission_codename:
            return Response(
                {'error': 'Permission codename is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate permission exists
        if not Permission.objects.filter(codename=permission_codename).exists():
            return Response(
                {'error': 'Invalid permission codename'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update override
        user_role.permission_overrides[permission_codename] = granted
        user_role.save()
        
        return Response({
            'message': f'Permission override set successfully',
            'permission': permission_codename,
            'granted': granted
        })
    
    @action(detail=True, methods=['delete'])
    def remove_permission_override(self, request, pk=None):
        """Remove individual permission override for a user"""
        user_role = self.get_object()
        permission_codename = request.data.get('permission')
        
        if permission_codename in user_role.permission_overrides:
            del user_role.permission_overrides[permission_codename]
            user_role.save()
            
            return Response({'message': 'Permission override removed successfully'})
        
        return Response(
            {'error': 'Permission override not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class PublicRoleViewSet(viewsets.ModelViewSet):
    """Manage public (unauthenticated) user permissions"""
    serializer_class = PublicRoleSerializer
    permission_classes = [CanConfigureLimits]
    
    def get_queryset(self):
        return PublicRole.objects.filter(pk=1)
    
    def get_object(self):
        return PublicRole.load()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current public permissions"""
        public_role = PublicRole.load()
        serializer = self.get_serializer(public_role)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_permissions(self, request):
        """Update public permissions"""
        public_role = PublicRole.load()
        permission_ids = request.data.get('permission_ids', [])
        
        # Validate permission IDs
        valid_permissions = Permission.objects.filter(id__in=permission_ids)
        if len(valid_permissions) != len(permission_ids):
            return Response(
                {'error': 'Some permission IDs are invalid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        public_role.permissions.set(valid_permissions)
        
        serializer = self.get_serializer(public_role)
        return Response(serializer.data)


class GlobalSettingsViewSet(viewsets.ModelViewSet):
    """Manage global system settings"""
    serializer_class = GlobalSettingsSerializer
    permission_classes = [CanConfigureLimits]
    
    def get_queryset(self):
        return GlobalSettings.objects.filter(pk=True)
    
    def get_object(self):
        return GlobalSettings.load()
    
    def perform_update(self, serializer):
        """Track who updated the settings"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current global settings"""
        settings = GlobalSettings.load()
        serializer = self.get_serializer(settings)
        return Response(serializer.data) 