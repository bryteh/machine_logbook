from rest_framework import serializers
from .models import Issue, Remedy, Attachment, ManufacturingMachine, ManufacturingDepartment, UserRole


class MachineSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.CharField(source='department.department_id', read_only=True)
    
    class Meta:
        model = ManufacturingMachine
        fields = ['machine_id', 'machine_number', 'model', 'status', 'department_id', 'department_name']


class DepartmentSerializer(serializers.ModelSerializer):
    machine_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ManufacturingDepartment
        fields = ['department_id', 'name', 'is_subcontracted', 'efficiency_pct', 'machine_count']
    
    def get_machine_count(self, obj):
        return ManufacturingMachine.objects.filter(department=obj).count()


class UserRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['username', 'role', 'can_view_costs', 'can_view_external_contacts']


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.ReadOnlyField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ['id', 'file_url', 'file_name', 'file_type', 'purpose', 'uploaded_at']
    
    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class RemedySerializer(serializers.ModelSerializer):
    technician_display_name = serializers.SerializerMethodField()
    phone_display = serializers.SerializerMethodField()
    cost_display = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Remedy
        fields = [
            'id', 'description', 'technician_name', 'is_external', 'phone_number',
            'parts_purchased', 'labor_cost', 'parts_cost', 'total_cost',
            'created_at', 'technician_display_name', 'phone_display', 'cost_display',
            'attachments'
        ]
    
    def get_technician_display_name(self, obj):
        """Hide external technician names based on user permissions"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return "External Technician" if obj.is_external else obj.technician_name
        
        try:
            user_role = request.user.role
            if obj.is_external and not user_role.can_view_external_contacts:
                return "External Technician"
        except UserRole.DoesNotExist:
            if obj.is_external:
                return "External Technician"
        
        return obj.technician_name
    
    def get_phone_display(self, obj):
        """Hide phone numbers based on user permissions"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None if obj.is_external else obj.phone_number
        
        try:
            user_role = request.user.role
            if obj.is_external and not user_role.can_view_external_contacts:
                return "***-***-****"
        except UserRole.DoesNotExist:
            if obj.is_external:
                return "***-***-****"
        
        return obj.phone_number
    
    def get_cost_display(self, obj):
        """Hide costs based on user permissions"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            user_role = request.user.role
            if not user_role.can_view_costs:
                return None
        except UserRole.DoesNotExist:
            return None
        
        return {
            'labor_cost': obj.labor_cost,
            'parts_cost': obj.parts_cost,
            'total_cost': obj.total_cost
        }


class IssueListSerializer(serializers.ModelSerializer):
    machine_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    remedies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'id', 'auto_title', 'category', 'priority', 'status', 'alarm_code',
            'machine_id_ref', 'machine_name', 'department_name', 'is_runnable',
            'reported_by', 'created_at', 'remedies_count', 'downtime_hours'
        ]
    
    def get_machine_name(self, obj):
        return obj.machine_name
    
    def get_department_name(self, obj):
        return obj.department_name
    
    def get_remedies_count(self, obj):
        return obj.remedies.count()


class IssueDetailSerializer(serializers.ModelSerializer):
    machine = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    remedies = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Issue
        fields = [
            'id', 'category', 'priority', 'alarm_code', 'description', 'is_runnable',
            'auto_title', 'ai_summary', 'status', 'machine_id_ref', 'reported_by',
            'downtime_start', 'downtime_end', 'downtime_hours', 'created_at', 'updated_at',
            'machine', 'department', 'remedies', 'attachments'
        ]
    
    def get_machine(self, obj):
        machine = obj.machine
        if machine:
            return {
                'machine_id': machine.machine_id,
                'machine_number': machine.machine_number,
                'model': machine.model,
                'status': machine.status
            }
        return {'machine_id': obj.machine_id_ref, 'model': 'Unknown'}
    
    def get_department(self, obj):
        department = obj.department
        if department:
            return {
                'department_id': department.department_id,
                'name': department.name
            }
        return {'name': 'Unknown'}
    
    def get_remedies(self, obj):
        """Get remedies ordered by creation time (latest first)"""
        remedies = obj.remedies.all().order_by('-created_at')
        return RemedySerializer(remedies, many=True, context=self.context).data


class IssueCreateSerializer(serializers.ModelSerializer):
    problem_guide = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'id', 'category', 'priority', 'alarm_code', 'description', 'is_runnable',
            'machine_id_ref', 'reported_by', 'problem_guide'
        ]
    
    def get_problem_guide(self, obj):
        """Return problem description guide"""
        return """Problem Description Guide:
1. What happened? (Brief description)
2. When did it occur? (Date/time)
3. Machine behavior observed
4. Error codes/alarms (if any)
5. Impact on production
6. Safety concerns (if any)"""
    
    def create(self, validated_data):
        issue = Issue.objects.create(**validated_data)
        return issue


class RemedyCreateSerializer(serializers.ModelSerializer):
    remedy_guide = serializers.SerializerMethodField()
    
    class Meta:
        model = Remedy
        fields = [
            'description', 'technician_name', 'is_external', 'phone_number',
            'is_machine_runnable', 'parts_purchased', 'labor_cost', 'parts_cost', 'remedy_guide'
        ]
    
    def get_remedy_guide(self, obj):
        """Return remedy description guide"""
        return """Remedy Description Guide:
1. Root cause identified
2. Actions taken
3. Parts replaced/purchased (list with quantities)
4. Tools/equipment used
5. Time taken to complete
6. Testing performed
7. Preventive measures recommended"""
    
    def validate(self, data):
        # Phone number validation for external technicians
        if data.get('is_external') and not data.get('phone_number'):
            raise serializers.ValidationError({
                'phone_number': 'Phone number is required for external technicians.'
            })
        return data


class AttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new attachments"""
    
    class Meta:
        model = Attachment
        fields = ['issue', 'remedy', 'file', 'file_type', 'purpose']
    
    def validate(self, data):
        # Ensure attachment is linked to either issue or remedy
        if not data.get('issue') and not data.get('remedy'):
            raise serializers.ValidationError(
                "Attachment must be linked to either an issue or remedy"
            )
        return data


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""
    open_issues = serializers.IntegerField()
    on_hold_issues = serializers.IntegerField()
    resolved_issues = serializers.IntegerField()
    avg_downtime = serializers.FloatField()
    trend_data = serializers.ListField(
        child=serializers.DictField()
    ) 