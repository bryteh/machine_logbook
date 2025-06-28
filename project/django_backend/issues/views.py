from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Issue, Remedy, Attachment, ManufacturingMachine, ManufacturingDepartment, UserRole
from .serializers import (
    IssueListSerializer, IssueDetailSerializer, IssueCreateSerializer,
    RemedySerializer, RemedyCreateSerializer, AttachmentSerializer,
    MachineSerializer, DepartmentSerializer, UserRoleSerializer
)
from .services import AIService, OCRService, FileService





class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManufacturingDepartment.objects.all()
    serializer_class = DepartmentSerializer
    
    @action(detail=True, methods=['get'])
    def dashboard_metrics(self, request, pk=None):
        """Get department-specific dashboard metrics"""
        department = self.get_object()
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Filter issues for this department
        department_issues = Issue.objects.filter(
            machine_id_ref__startswith=department.department_id
        ).filter(created_at__gte=start_date)
        
        # Check user permissions for cost data
        can_view_costs = False
        if request.user.is_authenticated:
            try:
                user_role = request.user.role
                can_view_costs = user_role.can_view_costs
            except UserRole.DoesNotExist:
                pass
        
        metrics = {
            'department_id': department.department_id,
            'department_name': department.name,
            'total_issues': department_issues.count(),
            'open_cases': department_issues.filter(status__in=['open', 'in_progress']).count(),
            'resolved_cases': department_issues.filter(status='resolved').count(),
            'on_hold_cases': department_issues.filter(status='on_hold').count(),
            'total_downtime_hours': sum([issue.downtime_hours for issue in department_issues]),
            'avg_resolution_time': self._calculate_avg_resolution_time(department_issues),
            'status_breakdown': self._get_status_breakdown(department_issues),
            'priority_breakdown': self._get_priority_breakdown(department_issues),
        }
        
        if can_view_costs:
            total_costs = 0
            for issue in department_issues:
                for remedy in issue.remedies.all():
                    if remedy.total_cost:
                        total_costs += remedy.total_cost
            metrics['total_cost'] = float(total_costs)
            metrics['avg_cost_per_issue'] = float(total_costs / max(department_issues.count(), 1))
        
        return Response(metrics)
    
    def _calculate_avg_resolution_time(self, issues):
        """Calculate average resolution time in hours"""
        resolved_issues = issues.filter(status='resolved', downtime_end__isnull=False)
        if not resolved_issues:
            return 0
        
        total_hours = sum([issue.downtime_hours for issue in resolved_issues])
        return round(total_hours / resolved_issues.count(), 2)
    
    def _get_status_breakdown(self, issues):
        """Get breakdown by status"""
        return {
            'open': issues.filter(status='open').count(),
            'in_progress': issues.filter(status='in_progress').count(),
            'on_hold': issues.filter(status='on_hold').count(),
            'resolved': issues.filter(status='resolved').count(),
        }
    
    def _get_priority_breakdown(self, issues):
        """Get breakdown by priority"""
        return {
            'low': issues.filter(priority='low').count(),
            'medium': issues.filter(priority='medium').count(),
            'high': issues.filter(priority='high').count(),
            'critical': issues.filter(priority='critical').count(),
        }


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManufacturingMachine.objects.all()
    serializer_class = MachineSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for machine issues"""
    queryset = Issue.objects.prefetch_related('remedies', 'attachments')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'machine_id_ref', 'is_runnable']
    search_fields = ['auto_title', 'description', 'alarm_code']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return IssueListSerializer
        elif self.action == 'create':
            return IssueCreateSerializer
        else:
            return IssueDetailSerializer

    def perform_create(self, serializer):
        """Create issue and process with AI if available"""
        try:
            issue = serializer.save()
            
            # Generate a basic title if none exists
            if not issue.auto_title:
                issue.auto_title = f"{issue.category.title()} Issue - {issue.machine_id_ref}"
            
            # Process with AI in background (or immediately for MVP)
            try:
                ai_summary, auto_title = AIService.generate_summary_and_title(
                    description=issue.description,
                    alarm_code=issue.alarm_code,
                    category=issue.category
                )
                issue.ai_summary = ai_summary
                if auto_title:
                    issue.auto_title = auto_title
                issue.save()
            except Exception as e:
                # Log error but don't fail the creation
                print(f"AI processing failed: {e}")
                # Save the basic title
                issue.save()
                
        except Exception as e:
            print(f"Issue creation failed: {e}")
            print(f"Serializer data: {serializer.validated_data}")
            raise

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Department filtering
        department = self.request.query_params.get('department', None)
        if department:
            # Filter by machine_id_ref starting with department_id
            queryset = queryset.filter(machine_id_ref__startswith=department)
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Priority filtering
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update issue status with automatic downtime tracking"""
        issue = self.get_object()
        new_status = request.data.get('status')
        
        if new_status:
            old_status = issue.status
            issue.status = new_status
            
            # Handle downtime tracking
            if new_status == 'in_progress' and not issue.downtime_start:
                issue.downtime_start = timezone.now()
            elif new_status == 'resolved' and issue.downtime_start and not issue.downtime_end:
                issue.downtime_end = timezone.now()
            elif new_status in ['open', 'on_hold'] and old_status == 'resolved':
                # Reopening issue
                issue.downtime_end = None
            
            issue.save()
        
        serializer = self.get_serializer(issue)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_remedy(self, request, pk=None):
        """Add a remedy to an issue"""
        issue = self.get_object()
        serializer = RemedyCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            remedy = serializer.save(issue=issue)
            
            # Automatically set status to in_progress when remedy is added
            if issue.status in ['open', 'on_hold']:
                issue.status = 'in_progress'
                if not issue.downtime_start and not issue.is_runnable:
                    issue.downtime_start = timezone.now()
                issue.save()
            
            # Update issue runnability based on remedy
            if remedy.is_machine_runnable and not issue.is_runnable:
                # Machine becomes runnable after remedy
                issue.is_runnable = True
                if issue.downtime_start and not issue.downtime_end:
                    issue.downtime_end = timezone.now()
                issue.save()
            elif not remedy.is_machine_runnable and issue.is_runnable:
                # Machine becomes not runnable after remedy (rare case)
                issue.is_runnable = False
                if not issue.downtime_start:
                    issue.downtime_start = timezone.now()
                issue.downtime_end = None
                issue.save()
            
            return Response(
                RemedySerializer(remedy, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add an attachment to an issue"""
        issue = self.get_object()
        serializer = AttachmentSerializer(data=request.data)
        
        if serializer.is_valid():
            attachment = serializer.save(issue=issue)
            return Response(AttachmentSerializer(attachment).data, 
                          status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def improve_remedy_description(request):
    """Improve remedy description using AI"""
    try:
        data = json.loads(request.body)
        description = data.get('description', '')
        
        if not description:
            return JsonResponse({'error': 'Description is required'}, status=400)
        
        improved_description = AIService.improve_remedy_description(description)
        
        return JsonResponse({
            'improved_description': improved_description
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  
@require_http_methods(["GET"])
def dashboard_metrics(request):
    """Get dashboard metrics with optional department filtering"""
    try:
        days = int(request.GET.get('days', 30))
        department = request.GET.get('department')
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        issues_qs = Issue.objects.filter(created_at__gte=start_date)
        
        # Apply department filter if specified
        if department:
            issues_qs = issues_qs.filter(machine_id_ref__startswith=department)
        
        # Basic metrics
        total_issues = issues_qs.count()
        open_issues = issues_qs.filter(status__in=['open', 'in_progress']).count()
        resolved_issues = issues_qs.filter(status='resolved').count()
        on_hold_issues = issues_qs.filter(status='on_hold').count()
        high_priority_issues = issues_qs.filter(priority='high').count()
        
        # Downtime calculation
        total_downtime_hours = 0
        for issue in issues_qs:
            if issue.downtime_hours:
                total_downtime_hours += issue.downtime_hours
        
        avg_downtime_per_issue = round(total_downtime_hours / max(total_issues, 1), 2)
        
        # Daily trend data
        daily_trend = []
        current_date = end_date.date()
        
        for i in range(days):
            date = current_date - timedelta(days=days-1-i)
            day_issues = issues_qs.filter(created_at__date=date)
            daily_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'issues': day_issues.count(),
                'resolved': day_issues.filter(status='resolved').count()
            })
        
        # Department breakdown
        department_breakdown = []
        departments = ManufacturingDepartment.objects.all()
        
        for dept in departments:
            dept_issues = issues_qs.filter(machine_id_ref__startswith=dept.department_id)
            dept_downtime = sum([issue.downtime_hours or 0 for issue in dept_issues])
            
            # Add cost data - temporarily allow all users to view costs for testing
            total_cost = 0
            for issue in dept_issues:
                for remedy in issue.remedies.all():
                    if remedy.total_cost:
                        total_cost += remedy.total_cost
            
            dept_data = {
                'department_id': dept.department_id,
                'name': dept.name,
                'total_issues': dept_issues.count(),
                'open_issues': dept_issues.filter(status__in=['open', 'in_progress']).count(),
                'resolved_issues': dept_issues.filter(status='resolved').count(),
                'downtime_hours': round(dept_downtime, 2),
                'total_cost': float(total_cost)
            }
            
            department_breakdown.append(dept_data)
        
        # Calculate overall cost metrics - temporarily allow all users to view costs
        total_cost = 0
        for issue in issues_qs:
            for remedy in issue.remedies.all():
                if remedy.total_cost:
                    total_cost += remedy.total_cost
        
        metrics = {
            'total_issues': total_issues,
            'open_issues': open_issues,
            'resolved_issues': resolved_issues,
            'on_hold_issues': on_hold_issues,
            'total_downtime_hours': round(total_downtime_hours, 2),
            'avg_downtime_per_issue': avg_downtime_per_issue,
            'daily_trend': daily_trend,
            'department_breakdown': department_breakdown,
            'total_cost': float(total_cost),
            'avg_cost_per_issue': float(total_cost / max(total_issues, 1)),
            'high_priority_issues': high_priority_issues
        }
        
        return JsonResponse(metrics)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def improve_description(request):
    """Improve issue description using AI"""
    try:
        description = request.data.get('description', '')
        alarm_code = request.data.get('alarm_code', '')
        
        if not description:
            return Response({'error': 'Description is required'}, status=400)
        
        improved_description = AIService.improve_issue_description(
            description=description,
            alarm_code=alarm_code
        )
        
        return Response({
            'improved_description': improved_description
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=500) 