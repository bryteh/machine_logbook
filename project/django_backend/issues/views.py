from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import (
    CanViewDashboard, CanCRUDIssues, CanCRUDRemedies, CanMarkResolved,
    IsPublicOrAuthenticated, HasPermission, CanGenerateReports
)
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
import json
import logging

from .models import Issue, Remedy, Attachment, ManufacturingMachine, ManufacturingDepartment, UserRole
from .serializers import (
    IssueListSerializer, IssueDetailSerializer, IssueCreateSerializer,
    RemedySerializer, RemedyCreateSerializer, AttachmentSerializer, AttachmentCreateSerializer,
    MachineSerializer, DepartmentSerializer, UserRoleSerializer
)
from .services import AIService, OCRService, FileService
from .media_processor import MediaProcessor
from .report_generator import MaintenanceReportGenerator

logger = logging.getLogger(__name__)


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
            except (UserRole.DoesNotExist, AttributeError):
                # Default to no access if UserRole doesn't exist or user doesn't have role
                can_view_costs = False
        
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
            queryset = queryset.filter(department__department_id=department_id)
        return queryset.order_by('machine_number')


class RemedyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing remedies"""
    serializer_class = RemedySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        """
        Override permissions to allow public access for most actions
        """
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'add_attachment', 'delete_attachment']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            return Remedy.objects.filter(issue_id=issue_id)
        return Remedy.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RemedyCreateSerializer
        
        # Use different serializers based on authentication status
        from django.contrib.auth.models import AnonymousUser
        if isinstance(self.request.user, AnonymousUser):
            # For updates, use serializer that includes phone_number and is_external
            if self.action in ['update', 'partial_update']:
                from .serializers import PublicRemedyUpdateSerializer
                return PublicRemedyUpdateSerializer
            else:
                from .serializers import PublicRemedySerializer
                return PublicRemedySerializer
        else:
            from .serializers import FullRemedySerializer
            return FullRemedySerializer
    
    def perform_create(self, serializer):
        """Create remedy and handle issue updates"""
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, id=issue_id)
        remedy = serializer.save(issue=issue)
        
        # Update issue status when remedy is added
        if issue.status in ['open', 'on_hold']:
            issue.status = 'in_progress'
            if not issue.downtime_start and not issue.is_runnable:
                issue.downtime_start = timezone.now()
            issue.save()
        
        # Update issue runnability based on remedy
        if remedy.is_machine_runnable and not issue.is_runnable:
            issue.is_runnable = True
            if issue.downtime_start and not issue.downtime_end:
                issue.downtime_end = timezone.now()
            issue.save()
        elif not remedy.is_machine_runnable and issue.is_runnable:
            issue.is_runnable = False
            if not issue.downtime_start:
                issue.downtime_start = timezone.now()
            issue.downtime_end = None
            issue.save()

    def perform_update(self, serializer):
        """Update remedy and handle issue status changes"""
        remedy = serializer.save()
        issue = remedy.issue
        
        # Update issue runnability based on updated remedy
        if remedy.is_machine_runnable and not issue.is_runnable:
            issue.is_runnable = True
            if issue.downtime_start and not issue.downtime_end:
                issue.downtime_end = timezone.now()
            issue.save()
        elif not remedy.is_machine_runnable and issue.is_runnable:
            issue.is_runnable = False
            if not issue.downtime_start:
                issue.downtime_start = timezone.now()
            issue.downtime_end = None
            issue.save()
    
    def perform_destroy(self, instance):
        """Delete remedy and handle any cleanup"""
        issue = instance.issue
        instance.delete()
        
        # If this was the last remedy and machine is not runnable, update issue status
        if not issue.remedies.exists() and not issue.is_runnable:
            if issue.status == 'in_progress':
                issue.status = 'open'
                issue.save()

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, issue_pk=None, pk=None):
        """Add an attachment to a remedy with media processing"""
        remedy = self.get_object()
        
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process the uploaded file
            processor = MediaProcessor()
            processed_file = processor.process_file(uploaded_file)
            
            # Determine file type from original file
            import mimetypes
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if mime_type and mime_type.startswith('image/'):
                detected_file_type = 'image'
            elif mime_type and mime_type.startswith('video/'):
                detected_file_type = 'video'
            else:
                detected_file_type = 'other'
            
            # Extract form data properly for multipart uploads
            data = {
                'remedy': remedy.id,
                'file': processed_file,
                'file_type': detected_file_type,
                'purpose': request.data.get('purpose', 'other')
            }
            
            serializer = AttachmentCreateSerializer(data=data)
            
            if serializer.is_valid():
                attachment = serializer.save()
                logger.info(f"Processed and saved attachment for remedy {remedy.id}: {attachment.file.name}")
                return Response(AttachmentSerializer(attachment).data, 
                              status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as e:
            logger.error(f"Media processing error for remedy {remedy.id}: {str(e)}")
            return Response({'error': f'Media processing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error processing attachment for remedy {remedy.id}: {str(e)}")
            return Response({'error': 'File processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, issue_pk=None, pk=None, attachment_id=None):
        """Delete a specific attachment from a remedy"""
        remedy = self.get_object()
        
        try:
            attachment = Attachment.objects.get(id=attachment_id, remedy=remedy)
            
            # Delete the file from storage
            if attachment.file:
                try:
                    attachment.file.delete(save=False)
                except Exception as e:
                    logger.warning(f"Failed to delete file for attachment {attachment_id}: {str(e)}")
            
            # Delete the attachment record
            attachment.delete()
            
            return Response({'message': 'Attachment deleted successfully'}, status=status.HTTP_200_OK)
            
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting attachment {attachment_id}: {str(e)}")
            return Response({'error': 'Failed to delete attachment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for machine issues"""
    queryset = Issue.objects.prefetch_related('remedies__attachments', 'attachments')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'machine_id_ref', 'is_runnable']
    search_fields = ['auto_title', 'description', 'alarm_code']
    ordering = ['-created_at']
    permission_classes = [IsPublicOrAuthenticated]

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
        """Add an attachment to an issue with media processing"""
        issue = self.get_object()
        
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process the uploaded file
            processor = MediaProcessor()
            processed_file = processor.process_file(uploaded_file)
            
            # Determine file type from original file
            import mimetypes
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if mime_type and mime_type.startswith('image/'):
                detected_file_type = 'image'
            elif mime_type and mime_type.startswith('video/'):
                detected_file_type = 'video'
            else:
                detected_file_type = 'other'
            
            # Extract form data properly for multipart uploads
            data = {
                'issue': issue.id,
                'file': processed_file,
                'file_type': detected_file_type,
                'purpose': request.data.get('purpose', 'alarm_screen')
            }
            
            serializer = AttachmentCreateSerializer(data=data)
            
            if serializer.is_valid():
                attachment = serializer.save()
                logger.info(f"Processed and saved attachment for issue {issue.id}: {attachment.file.name}")
                return Response(AttachmentSerializer(attachment).data, 
                              status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as e:
            logger.error(f"Media processing error for issue {issue.id}: {str(e)}")
            return Response({'error': f'Media processing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error processing attachment for issue {issue.id}: {str(e)}")
            return Response({'error': 'File processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """Delete a specific attachment from an issue"""
        issue = self.get_object()
        
        try:
            attachment = Attachment.objects.get(id=attachment_id, issue=issue)
            
            # Delete the file from storage
            if attachment.file:
                try:
                    attachment.file.delete(save=False)
                except Exception as e:
                    logger.warning(f"Failed to delete file for attachment {attachment_id}: {str(e)}")
            
            # Delete the attachment record
            attachment.delete()
            
            return Response({'message': 'Attachment deleted successfully'}, status=status.HTTP_200_OK)
            
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting attachment {attachment_id}: {str(e)}")
            return Response({'error': 'Failed to delete attachment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[CanGenerateReports])
    def generate_report(self, request, pk=None):
        """Generate a PDF maintenance report for the issue"""
        issue = self.get_object()
        
        # Check if issue is resolved
        if issue.status != 'resolved':
            return Response(
                {'error': 'Reports can only be generated for resolved issues'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generator = MaintenanceReportGenerator()
            pdf_content = generator.generate_pdf_report(issue, authorized_by_user=request.user)
            
            # Log the report generation activity
            from .models import AuditLog
            AuditLog.log_activity(
                user=request.user,
                action='report_generated',
                description=f'Generated maintenance report for issue {issue.auto_title} (ID: {issue.id})',
                issue=issue,
                request=request,
                report_type='maintenance_pdf'
            )
            
            response = generator.create_download_response(pdf_content, issue)
            return response
        except Exception as e:
            logger.error(f"Error generating report for issue {issue.id}: {str(e)}")
            return Response(
                {'error': 'Failed to generate report'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """Get audit logs for issues"""
        try:
            # Get query parameters
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            action_filter = request.GET.get('action', None)
            user_filter = request.GET.get('user', None)
            
            # Build query
            from .models import AuditLog
            queryset = AuditLog.objects.all()
            
            if action_filter:
                queryset = queryset.filter(action=action_filter)
            
            if user_filter:
                queryset = queryset.filter(user__username__icontains=user_filter)
            
            # Apply pagination
            total_count = queryset.count()
            logs = queryset.order_by('-created_at')[offset:offset + limit]
            
            # Serialize the data
            logs_data = []
            for log in logs:
                logs_data.append({
                    'id': str(log.id),
                    'user': log.user.username if log.user else 'System',
                    'action': log.get_action_display(),
                    'action_code': log.action,
                    'description': log.description,
                    'issue_id': str(log.issue.id) if log.issue else None,
                    'issue_title': log.issue.auto_title if log.issue else None,
                    'remedy_id': str(log.remedy.id) if log.remedy else None,
                    'ip_address': log.ip_address,
                    'metadata': log.metadata,
                    'created_at': log.created_at.isoformat(),
                })
            
            return Response({
                'results': logs_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_next': offset + limit < total_count,
                'has_previous': offset > 0
            })
            
        except Exception as e:
            logger.error(f"Error fetching audit logs: {str(e)}")
            return Response(
                {'error': 'Failed to fetch audit logs'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


@api_view(['GET'])
def dashboard_metrics(request):
    """Get dashboard metrics with optional department filtering"""
    # Check if user has permission to view dashboard
    from django.contrib.auth.models import AnonymousUser
    
    if isinstance(request.user, AnonymousUser):
        # Anonymous users cannot view dashboard
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Authenticated users: check permissions (allow superusers automatically)
    if not request.user.is_superuser:
        if hasattr(request.user, 'role') and request.user.role:
            if not request.user.role.has_permission('view_dashboard'):
                return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
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
            
            # Add cost data only for users with permission
            dept_total_cost = 0
            if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role and 
                (request.user.role.has_permission('view_costs') or request.user.role.can_view_costs)):
                for issue in dept_issues:
                    for remedy in issue.remedies.all():
                        if remedy.total_cost:
                            dept_total_cost += remedy.total_cost
            
            dept_data = {
                'department_id': dept.department_id,
                'name': dept.name,
                'total_issues': dept_issues.count(),
                'open_issues': dept_issues.filter(status__in=['open', 'in_progress']).count(),
                'resolved_issues': dept_issues.filter(status='resolved').count(),
                'downtime_hours': round(dept_downtime, 2),
            }
            
            # Only include cost data if user has permission
            if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role and 
                (request.user.role.has_permission('view_costs') or request.user.role.can_view_costs)):
                dept_data['total_cost'] = float(dept_total_cost)
                
            department_breakdown.append(dept_data)
        
        # Calculate overall cost metrics only for users with permission
        total_cost = 0
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role and 
            (request.user.role.has_permission('view_costs') or request.user.role.can_view_costs)):
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
            'high_priority_issues': high_priority_issues
        }
        
        # Only include cost data if user has permission
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role and 
            (request.user.role.has_permission('view_costs') or request.user.role.can_view_costs)):
            metrics['total_cost'] = float(total_cost)
            metrics['avg_cost_per_issue'] = float(total_cost / max(total_issues, 1))
        
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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                
                # Get user role and permissions
                role_info = None
                if hasattr(user, 'role') and user.role:
                    role_info = {
                        'role': user.role.role.codename if user.role.role else None,
                        'role_name': user.role.role.name if user.role.role else None,
                        'permissions': user.role.get_all_permissions(),
                        'can_view_costs': user.role.can_view_costs,
                        'can_view_external_contacts': user.role.can_view_external_contacts
                    }
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'role': role_info
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Account is disabled'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get user role and permissions
        role_info = None
        if hasattr(user, 'role') and user.role:
            role_info = {
                'role': user.role.role.codename,
                'role_name': user.role.role.name,
                'permissions': user.role.get_all_permissions(),
                'can_view_costs': user.role.can_view_costs,
                'can_view_external_contacts': user.role.can_view_external_contacts
            }
        
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': role_info
        })


class CSRFTokenView(APIView):
    """Get CSRF token for authenticated requests"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get CSRF token"""
        token = get_token(request)
        return Response({'csrfToken': token})


@require_http_methods(["POST"])
def generate_report_view(request, issue_id):
    """Generate PDF report for an issue"""
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check permissions
        if not hasattr(request.user, 'role') or not request.user.role:
            return JsonResponse({'error': 'No role assigned'}, status=403)
        
        if not request.user.role.has_permission('generate_reports'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        issue = get_object_or_404(Issue, id=issue_id)
        
        # Check if issue is resolved
        if issue.status != 'resolved':
            return JsonResponse(
                {'error': 'Reports can only be generated for resolved issues'}, 
                status=400
            )
        
        generator = MaintenanceReportGenerator()
        pdf_content = generator.generate_pdf_report(issue, authorized_by_user=request.user)
        
        # Log the report generation activity
        from .models import AuditLog
        AuditLog.log_activity(
            user=request.user,
            action='report_generated',
            description=f'Generated maintenance report for issue {issue.auto_title} (ID: {issue.id})',
            issue=issue,
            request=request,
            report_type='maintenance_pdf'
        )
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="maintenance_report_{issue.id}.pdf"'
        response['Content-Length'] = len(pdf_content)
        
        return response
        
    except Issue.DoesNotExist:
        return JsonResponse(
            {'error': 'Issue not found'}, 
            status=404
        )
    except Exception as e:
        logger.error(f"Error generating report for issue {issue_id}: {str(e)}")
        return JsonResponse(
            {'error': 'Failed to generate report'}, 
            status=500
        )