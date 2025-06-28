from django.contrib import admin
from .models import Issue, Remedy, Attachment, ManufacturingMachine, ManufacturingDepartment, UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'can_view_costs', 'can_view_external_contacts']
    list_filter = ['role', 'can_view_costs', 'can_view_external_contacts']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['department_access']


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