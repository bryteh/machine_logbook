import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('technician', 'Technician'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    can_view_costs = models.BooleanField(default=False)
    can_view_external_contacts = models.BooleanField(default=False)
    department_access = models.ManyToManyField('ManufacturingDepartment', blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


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
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('software', 'Software'),
        ('maintenance', 'Maintenance'),
        ('calibration', 'Calibration'),
        ('safety', 'Safety'),
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