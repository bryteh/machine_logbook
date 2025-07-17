"""
Report Generation Service
Generates PDF reports from Excel templates for maintenance issues
"""

import os
import io
import uuid
from datetime import datetime
import pytz
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas


class MaintenanceReportGenerator:
    """Generates PDF maintenance reports using Excel template as reference"""
    
    def __init__(self):
        self.template_path = os.path.join(
            settings.BASE_DIR, 
            'templates', 
            'reports', 
            'Corrective_Maintenance_Service_Template.xlsx'
        )
        
    def generate_pdf_report(self, issue, authorized_by_user=None):
        """Generate PDF report for a given issue"""
        
        # Create a BytesIO buffer to receive PDF data
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for the 'flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.black
        )
        
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            alignment=1,  # Center alignment
            textColor=colors.black
        )
        
        address_style = ParagraphStyle(
            'AddressStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=1,  # Center alignment
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.black
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Generate unique document ID
        doc_id = f"CM-{issue.id.hex[:8].upper()}"
        
        # Company Header (centered)
        elements.append(Paragraph("ERABASE", title_style))
        elements.append(Paragraph("ERABASE INDUSTRY SDN BHD (276999-M)", company_style))
        elements.append(Paragraph("NO.23, JALAN ISTIMEWA 4, TAMAN PERINDUSTRIAN CEMERLANG, 81800 ULU TIRAM, JOHOR", address_style))
        elements.append(Paragraph("Tel: 07-861 6039   Email: enquiry@erabase.my  www.erabase.my", address_style))
        elements.append(Spacer(1, 12))
        
        # Document header (without "Corrective Maintenance Note:")
        header_data = [
            ["", "", "", f"Document#FRM/CM/1"],
            ["", "", "", "REV:00"],
            ["", "", "", f"ID: {doc_id}"]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Issue Details Section
        issue_data = [
            ["Department:", issue.department.name if issue.department else "N/A", "Machine:", issue.machine.model if issue.machine else "N/A"],
            ["Reported By:", issue.reported_by, "Contact No:", "N/A"],  # Contact field not in model yet
            ["Category:", issue.get_category_display(), "Priority:", issue.get_priority_display()],
            ["Date Time:", issue.created_at.strftime("%d/%m/%Y %H:%M"), "Machine Status:", "Running" if issue.is_runnable else "Down"],
        ]
        
        issue_table = Table(issue_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        issue_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # First column bold
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Third column bold
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(issue_table)
        elements.append(Spacer(1, 20))
        
        # Issue Description (use AI summary if available, otherwise use description)
        elements.append(Paragraph("Issue Description:", header_style))
        description_text = issue.ai_summary if issue.ai_summary else (issue.description or "No description provided")
        elements.append(Paragraph(description_text, normal_style))
        elements.append(Spacer(1, 20))
        
        # Remedies Section
        if issue.remedies.exists():
            elements.append(Paragraph("Remedies and Actions Taken:", header_style))
            elements.append(Spacer(1, 10))
            
            # Remedies table header
            remedy_headers = ["Date Time", "Task Performed", "Part Changed", "Machine Status", "Technician"]
            remedy_data = [remedy_headers]
            
            # Add remedy rows
            for remedy in issue.remedies.all():
                remedy_data.append([
                    remedy.created_at.strftime("%d/%m/%Y %H:%M"),
                    Paragraph(remedy.description, ParagraphStyle('RemedyTask', parent=normal_style, wordWrap='CJK', alignment=0)),
                    remedy.parts_purchased or "None",
                    "Running" if remedy.is_machine_runnable else "Down",
                    remedy.technician_name
                ])
            
            remedy_table = Table(remedy_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 1*inch, 1.1*inch])
            remedy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(remedy_table)
            elements.append(Spacer(1, 20))
        
        # Cost Summary (if costs exist)
        total_cost = sum(remedy.total_cost or 0 for remedy in issue.remedies.all())
        if total_cost > 0:
            elements.append(Paragraph("Cost Summary:", header_style))
            cost_data = [
                ["Total Labor Cost:", f"RM {sum(remedy.labor_cost or 0 for remedy in issue.remedies.all()):.2f}"],
                ["Total Parts Cost:", f"RM {sum(remedy.parts_cost or 0 for remedy in issue.remedies.all()):.2f}"],
                ["Total Cost:", f"RM {total_cost:.2f}"]
            ]
            
            cost_table = Table(cost_data, colWidths=[3*inch, 2*inch])
            cost_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ]))
            elements.append(cost_table)
            elements.append(Spacer(1, 20))
        
        # Downtime Summary
        if issue.downtime_hours and issue.downtime_hours > 0:
            elements.append(Paragraph("Downtime Summary:", header_style))
            downtime_data = [
                ["Total Downtime:", f"{issue.downtime_hours:.2f} hours"],
                ["Status:", issue.get_status_display()]
            ]
            
            downtime_table = Table(downtime_data, colWidths=[3*inch, 2*inch])
            downtime_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(downtime_table)
            elements.append(Spacer(1, 30))
        
        # Footer with authorized person and UTC+8 timezone
        # Get authorized person name
        authorized_name = "_" * 30  # Default blank line
        if authorized_by_user:
            if authorized_by_user.first_name and authorized_by_user.last_name:
                authorized_name = f"{authorized_by_user.first_name} {authorized_by_user.last_name}"
            else:
                authorized_name = authorized_by_user.username
        
        # Convert to UTC+8 (Malaysia time)
        malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
        current_time_malaysia = timezone.now().astimezone(malaysia_tz)
        
        footer_data = [
            ["Authorized by:", authorized_name, "", f"Date/Time Printed: {current_time_malaysia.strftime('%d/%m/%Y %H:%M')}"]
        ]
        
        footer_table = Table(footer_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2.5*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ]))
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it as HttpResponse
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def create_download_response(self, pdf_content, issue):
        """Create HTTP response for PDF download"""
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f"maintenance_report_{issue.id.hex[:8]}_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response 