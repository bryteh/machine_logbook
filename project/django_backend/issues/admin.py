from django.contrib import admin
from .models import (
    Issue, Remedy, Attachment, ManufacturingMachine, ManufacturingDepartment, 
    UserRole, Role, Permission, PublicRole, GlobalSettings, AuditLog
)

# RBAC Admin Classes

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'category', 'description']
    list_filter = ['category']
    search_fields = ['name', 'codename', 'description']
    ordering = ['category', 'name']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'is_active', 'user_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'codename', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_count(self, obj):
        return obj.userrole_set.count()
    user_count.short_description = 'Users'

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'can_view_costs', 'can_view_external_contacts', 'created_at']
    list_filter = ['role', 'can_view_costs', 'can_view_external_contacts', 'created_at']
    search_fields = ['user__username', 'user__email', 'role__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Assignment', {
            'fields': ('user', 'role')
        }),
        ('Legacy Permissions', {
            'fields': ('can_view_costs', 'can_view_external_contacts'),
            'description': 'These are legacy permission fields. Use role permissions for new setups.'
        }),
        ('Permission Overrides', {
            'fields': ('permission_overrides',),
            'description': 'JSON format: {"permission_codename": true/false}'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Override the default User admin to handle UserRole cascade deletion
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import transaction

# Unregister the default User admin and register our custom one
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin that properly handles UserRole cascade deletion"""
    
    def delete_model(self, request, obj):
        """Delete user and handle related UserRole properly"""
        with transaction.atomic():
            # Explicitly delete UserRole first to avoid constraint issues
            try:
                if hasattr(obj, 'role'):
                    obj.role.delete()
            except UserRole.DoesNotExist:
                pass
            except Exception as e:
                # If there's still an issue, try direct deletion
                UserRole.objects.filter(user=obj).delete()
            
            # Now delete the user
            super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Handle bulk deletion"""
        with transaction.atomic():
            # Get user IDs as a list first
            user_ids = list(queryset.values_list('id', flat=True))
            # Delete related UserRoles first
            if user_ids:
                UserRole.objects.filter(user_id__in=user_ids).delete()
            # Now delete the users
            super().delete_queryset(request, queryset)
    
    def get_deleted_objects(self, objs, request):
        """Override to show related UserRole objects that will be deleted"""
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        
        # Add UserRole information
        try:
            if not isinstance(objs, list):
                objs = [objs]
            
            # Get user IDs to avoid query object issues
            user_ids = []
            for obj in objs:
                if hasattr(obj, 'id'):
                    user_ids.append(obj.id)
            
            if user_ids:
                user_roles = UserRole.objects.filter(user_id__in=user_ids)
                if user_roles.exists():
                    deleted_objects.append("User Roles:")
                    for ur in user_roles:
                        try:
                            role_name = ur.role.name if ur.role else "No Role"
                            deleted_objects.append(f"  - {ur.user.username} → {role_name}")
                        except:
                            deleted_objects.append(f"  - UserRole ID {ur.id}")
        except Exception as e:
            # If there's any error, just skip showing UserRole info
            pass
        
        return deleted_objects, model_count, perms_needed, protected

@admin.register(PublicRole)
class PublicRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'permission_count']
    filter_horizontal = ['permissions']
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions Count'
    
    def has_add_permission(self, request):
        # Only allow one PublicRole instance
        return not PublicRole.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of PublicRole
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow editing of PublicRole
        return True

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'max_update_text_length', 'max_attachments_per_issue', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Text Limits', {
            'fields': ('max_update_text_length',)
        }),
        ('Attachment Limits', {
            'fields': ('max_attachments_per_issue', 'max_attachments_per_remedy', 'max_file_size_mb')
        }),
        ('Media Quality', {
            'fields': ('max_video_resolution_height', 'max_video_quality_crf')
        }),
        ('System Info', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Only allow one GlobalSettings instance
        return not GlobalSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of GlobalSettings
        return False
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['auto_title', 'category', 'priority', 'status', 'machine_id_ref', 'created_at']
    list_filter = ['status', 'category', 'priority', 'is_runnable', 'created_at']
    search_fields = ['auto_title', 'description', 'alarm_code', 'machine_id_ref']
    readonly_fields = ['id', 'ai_summary', 'downtime_hours', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'priority', 'alarm_code', 'machine_id_ref', 'reported_by')
        }),
        ('Issue Details', {
            'fields': ('description', 'auto_title', 'ai_summary', 'is_runnable')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'downtime_start', 'downtime_end', 'downtime_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Remedy)
class RemedyAdmin(admin.ModelAdmin):
    list_display = ['issue', 'technician_name', 'is_external', 'total_cost', 'created_at']
    list_filter = ['is_external', 'created_at']
    search_fields = ['technician_name', 'description', 'parts_purchased']
    readonly_fields = ['id', 'total_cost', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('issue', 'description', 'technician_name', 'is_external', 'phone_number')
        }),
        ('Parts & Costing', {
            'fields': ('parts_purchased', 'labor_cost', 'parts_cost', 'total_cost')
        }),
        ('Guidance', {
            'fields': ('problem_format_guide', 'remedy_format_guide'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['issue', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    readonly_fields = ['id', 'uploaded_at']


# For existing tables, we make them read-only in admin
@admin.register(ManufacturingMachine)
class ManufacturingMachineAdmin(admin.ModelAdmin):
    list_display = ['machine_number', 'model', 'status', 'department_id']
    list_filter = ['status', 'department_id']
    search_fields = ['machine_number', 'model', 'machine_id']
    readonly_fields = ['machine_id', 'department_id', 'machine_number', 'model', 'status', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ManufacturingDepartment)
class ManufacturingDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'department_id', 'is_subcontracted', 'efficiency_pct']
    list_filter = ['is_subcontracted']
    search_fields = ['name', 'department_id']
    readonly_fields = ['department_id', 'name', 'is_subcontracted', 'efficiency_pct', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description_short', 'issue_link', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at', 'user']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['id', 'user', 'action', 'description', 'issue', 'remedy', 'ip_address', 'user_agent', 'metadata', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action', 'description', 'created_at')
        }),
        ('Related Objects', {
            'fields': ('issue', 'remedy')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def description_short(self, obj):
        """Show shortened description"""
        if len(obj.description) > 100:
            return obj.description[:100] + "..."
        return obj.description
    description_short.short_description = 'Description'
    
    def issue_link(self, obj):
        """Show issue link if available"""
        if obj.issue:
            return f"Issue #{obj.issue.id.hex[:8]}"
        return "-"
    issue_link.short_description = 'Issue'
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of audit logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers (for cleanup)
        return request.user.is_superuser 