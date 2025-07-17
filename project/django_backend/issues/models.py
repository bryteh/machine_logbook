import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Permission(models.Model):
    """Individual permissions that can be granted"""
    name = models.CharField(max_length=50, unique=True)
    codename = models.CharField(max_length=50, unique=True)  # e.g., 'view_dashboard'
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, default='general')  # group permissions
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """Configurable roles with dynamic permissions"""
    name = models.CharField(max_length=50, unique=True)
    codename = models.CharField(max_length=50, unique=True)  # e.g., 'admin'
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)
    is_public_role = models.BooleanField(default=False)  # for unauthenticated users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def has_permission(self, permission_codename):
        """Check if role has a specific permission"""
        return self.permissions.filter(codename=permission_codename).exists()


class UserRole(models.Model):
    """Link users to roles with optional individual overrides"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    # Individual permission overrides (JSON format)
    permission_overrides = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Individual permission overrides: {permission_codename: true/false}"
    )
    
    # Legacy fields for compatibility
    can_view_costs = models.BooleanField(default=False)
    can_view_external_contacts = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    def has_permission(self, permission_codename):
        """Check if user has specific permission (override > role > default)"""
        # Check individual override first
        if permission_codename in self.permission_overrides:
            return self.permission_overrides[permission_codename]
        
        # Check role permission
        return self.role.has_permission(permission_codename)
    
    def get_all_permissions(self):
        """Get all permissions for this user (role + overrides)"""
        role_permissions = set(self.role.permissions.values_list('codename', flat=True))
        
        # Apply overrides
        for perm, granted in self.permission_overrides.items():
            if granted:
                role_permissions.add(perm)
            else:
                role_permissions.discard(perm)
        
        return list(role_permissions)


class PublicRole(models.Model):
    """Special model to define what public (unauthenticated) users can do"""
    permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Public Access Permissions"
        verbose_name_plural = "Public Access Permissions"
    
    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def has_permission(self, permission_codename):
        return self.permissions.filter(codename=permission_codename).exists()


class GlobalSettings(models.Model):
    """Singleton pattern for global settings"""
    id = models.BooleanField(primary_key=True, default=True)
    
    # Configurable limits
    max_update_text_length = models.IntegerField(default=2000)
    max_attachments_per_issue = models.IntegerField(default=10)
    max_attachments_per_remedy = models.IntegerField(default=5)
    max_video_resolution_height = models.IntegerField(default=720)
    max_video_quality_crf = models.IntegerField(default=28)
    max_file_size_mb = models.IntegerField(default=50)
    
    # System information
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"
    
    def save(self, *args, **kwargs):
        self.pk = True
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass  # Prevent deletion
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=True)
        return obj


class ManufacturingDepartment(models.Model):
    """
    Department model - connects to existing erabase_db table
    """
    department_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    is_subcontracted = models.BooleanField(default=False)
    efficiency_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manufacturing_department'
        managed = False  # Django won't manage this table (read-only)
    
    def __str__(self):
        return f"{self.department_id} - {self.name}"


class ManufacturingMachine(models.Model):
    """
    Machine model - connects to existing erabase_db table
    """
    machine_id = models.CharField(max_length=20, primary_key=True)
    department = models.ForeignKey(ManufacturingDepartment, on_delete=models.CASCADE, db_column='department_id')
    machine_number = models.CharField(max_length=50)
    model = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manufacturing_machine'
        managed = False  # Django won't manage this table (read-only)
    
    def __str__(self):
        return f"{self.machine_id} - {self.model}"


class Issue(models.Model):
    """
    Machine issue tracking model - simplified without FK constraints
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'), 
        ('on_hold', 'On Hold'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('alarm', 'Alarm'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('quality', 'Quality'),
        ('process', 'Process'),
        ('material_issue', 'Material Issue'),
        ('machine_setup', 'Machine Setup'),
        ('no_planning', 'No Planning'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Use simple string field to avoid FK constraint issues
    machine_id_ref = models.CharField(max_length=20, help_text="Reference to manufacturing_machine.machine_id")
    
    @property
    def machine(self):
        """Get the machine through the machine_id_ref"""
        try:
            return ManufacturingMachine.objects.get(machine_id=self.machine_id_ref)
        except ManufacturingMachine.DoesNotExist:
            return None
    
    @property 
    def department(self):
        """Get the department through the machine's department_id"""
        if self.machine:
            return self.machine.department
        return None
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    alarm_code = models.CharField(max_length=100, blank=True, null=True)
    alarm_ocr_text = models.TextField(blank=True, null=True)
    description = models.TextField()
    ai_summary = models.TextField(blank=True)
    auto_title = models.CharField(max_length=200, blank=True)
    is_runnable = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_by = models.CharField(max_length=100)
    downtime_start = models.DateTimeField(null=True, blank=True)
    downtime_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def machine_name(self):
        machine = self.machine
        if machine:
            # Return format: machine_number (model)
            if machine.machine_number and machine.model:
                return f"{machine.machine_number} ({machine.model})"
            elif machine.machine_number:
                return machine.machine_number
            elif machine.model:
                return machine.model
            else:
                return self.machine_id_ref
        return self.machine_id_ref
    
    @property
    def department_name(self):
        department = self.department
        return department.name if department else "Unknown"
    
    @property
    def downtime_hours(self):
        """Calculate current downtime in hours"""
        if not self.downtime_start:
            return 0
        
        # Ensure downtime_start is timezone-aware
        try:
            if timezone.is_naive(self.downtime_start):
                downtime_start = timezone.make_aware(self.downtime_start)
            else:
                downtime_start = self.downtime_start
        except Exception:
            return 0
        
        # If issue is resolved and we have downtime_end, return the final accumulated downtime
        if self.status == 'resolved' and self.downtime_end:
            try:
                if timezone.is_naive(self.downtime_end):
                    downtime_end = timezone.make_aware(self.downtime_end)
                else:
                    downtime_end = self.downtime_end
                
                delta = downtime_end - downtime_start
                return round(delta.total_seconds() / 3600, 4)
            except Exception:
                return 0
        
        # If machine is currently not runnable and issue is active, calculate ongoing downtime
        if not self.is_runnable and self.status in ['open', 'in_progress', 'on_hold']:
            try:
                if self.downtime_end:
                    # Use existing downtime_end if available
                    if timezone.is_naive(self.downtime_end):
                        end_time = timezone.make_aware(self.downtime_end)
                    else:
                        end_time = self.downtime_end
                else:
                    # Use current time for ongoing downtime
                    end_time = timezone.now()
                
                delta = end_time - downtime_start
                return round(delta.total_seconds() / 3600, 4)
            except Exception:
                return 0
        
        # If downtime has ended (machine is runnable but not resolved)
        if self.downtime_end:
            try:
                if timezone.is_naive(self.downtime_end):
                    downtime_end = timezone.make_aware(self.downtime_end)
                else:
                    downtime_end = self.downtime_end
                
                delta = downtime_end - downtime_start
                return round(delta.total_seconds() / 3600, 4)
            except Exception:
                return 0
        
        return 0

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.auto_title or 'Issue'} - {self.machine_id_ref}"
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        old_status = None
        
        # Get old status if updating
        if not is_new:
            try:
                old_issue = Issue.objects.get(pk=self.pk)
                old_status = old_issue.status
            except Issue.DoesNotExist:
                pass
        
        # Start downtime tracking when issue is created and machine is not runnable
        if not self.pk and not self.is_runnable and not self.downtime_start:
            self.downtime_start = timezone.now()
        
        # Handle downtime based on machine runnability
        if not self.is_runnable and not self.downtime_start and self.status in ['open', 'in_progress', 'on_hold']:
            # Start downtime if machine becomes not runnable
            self.downtime_start = timezone.now()
            self.downtime_end = None
        elif self.is_runnable and self.downtime_start and not self.downtime_end:
            # End downtime if machine becomes runnable
            self.downtime_end = timezone.now()
        elif not self.is_runnable and self.downtime_end:
            # Restart downtime if machine becomes not runnable again
            self.downtime_start = timezone.now()
            self.downtime_end = None
        
        # Handle status changes
        if self.status == 'resolved' and self.downtime_start and not self.downtime_end:
            self.downtime_end = timezone.now()
        elif self.status in ['open', 'in_progress', 'on_hold'] and not self.is_runnable and not self.downtime_start:
            self.downtime_start = timezone.now()
            self.downtime_end = None
        
        # Ensure auto_title is set
        if not self.auto_title:
            self.auto_title = f"{self.category.title()} Issue - {self.machine_id_ref}"
        
        super().save(*args, **kwargs)
        
        # Log audit events after save
        if is_new:
            # Log issue creation
            AuditLog.log_activity(
                user=None,  # Will be set by view when available
                action='issue_created',
                description=f'New issue created: {self.auto_title} for machine {self.machine_id_ref}',
                issue=self
            )
        elif old_status and old_status != self.status:
            # Log status change
            AuditLog.log_activity(
                user=None,  # Will be set by view when available
                action='status_changed' if self.status != 'resolved' else 'issue_resolved',
                description=f'Issue status changed from {old_status} to {self.status} for {self.auto_title}',
                issue=self,
                old_status=old_status,
                new_status=self.status
            )


class Remedy(models.Model):
    """
    Remedy/solution attempts for issues
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='remedies')
    description = models.TextField()
    technician_name = models.CharField(max_length=100)
    is_external = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_machine_runnable = models.BooleanField(default=False, help_text="Whether machine is still runnable after remedy")
    
    # New costing fields
    parts_purchased = models.TextField(blank=True, help_text="List of parts/items purchased for this remedy")
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Labor cost in currency")
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total parts cost in currency")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total remedy cost (auto-calculated)")
    
    # Guidance/template fields
    problem_format_guide = models.TextField(
        default="""Problem Description Guide:
1. What happened? (Brief description)
2. When did it occur? (Date/time)
3. Machine behavior observed
4. Error codes/alarms (if any)
5. Impact on production
6. Safety concerns (if any)""",
        help_text="Guide format for describing problems"
    )
    
    remedy_format_guide = models.TextField(
        default="""Remedy Description Guide:
1. Root cause identified
2. Actions taken
3. Parts replaced/purchased (list with quantities)
4. Tools/equipment used
5. Time taken to complete
6. Testing performed
7. Preventive measures recommended""",
        help_text="Guide format for remedy documentation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total cost
        if self.labor_cost and self.parts_cost:
            self.total_cost = self.labor_cost + self.parts_cost
        elif self.labor_cost:
            self.total_cost = self.labor_cost
        elif self.parts_cost:
            self.total_cost = self.parts_cost
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Remedy for {self.issue.auto_title} by {self.technician_name}"


class Attachment(models.Model):
    """
    File attachments for issues and remedies
    """
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    PURPOSE_CHOICES = [
        ('alarm_screen', 'Alarm Screen'),
        ('manual', 'Manual'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        blank=True, 
        null=True
    )
    remedy = models.ForeignKey(
        Remedy, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        blank=True, 
        null=True
    )
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='other')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_type} - {self.purpose}"
    
    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return None


class AuditLog(models.Model):
    """Audit log to track user activities"""
    ACTION_CHOICES = [
        ('issue_created', 'Issue Created'),
        ('issue_updated', 'Issue Updated'),
        ('issue_resolved', 'Issue Resolved'),
        ('issue_reopened', 'Issue Reopened'),
        ('remedy_added', 'Remedy Added'),
        ('remedy_updated', 'Remedy Updated'),
        ('remedy_deleted', 'Remedy Deleted'),
        ('report_generated', 'Report Generated'),
        ('status_changed', 'Status Changed'),
        ('attachment_added', 'Attachment Added'),
        ('attachment_deleted', 'Attachment Deleted'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('permission_changed', 'Permission Changed'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Related objects (optional)
    issue = models.ForeignKey('Issue', on_delete=models.SET_NULL, null=True, blank=True)
    remedy = models.ForeignKey('Remedy', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # For additional data
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['issue', '-created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.username if self.user else "Anonymous"
        return f"{user_name} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_activity(cls, user, action, description, issue=None, remedy=None, request=None, **metadata):
        """Helper method to create audit log entries"""
        ip_address = None
        user_agent = ""
        
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            user=user,
            action=action,
            description=description,
            issue=issue,
            remedy=remedy,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )