#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

# Write results to a file
with open('attachment_check_results.txt', 'w') as f:
    f.write("=== Database Check ===\n")
    f.write(f"Total Issues: {Issue.objects.count()}\n")
    f.write(f"Total Remedies: {Remedy.objects.count()}\n")
    f.write(f"Total Attachments: {Attachment.objects.count()}\n")
    f.write(f"Remedy Attachments: {Attachment.objects.filter(remedy__isnull=False).count()}\n")
    f.write(f"Issue Attachments: {Attachment.objects.filter(issue__isnull=False).count()}\n")
    
    f.write("\n=== Remedy Attachment Details ===\n")
    remedy_attachments = Attachment.objects.filter(remedy__isnull=False)
    for att in remedy_attachments:
        f.write(f"Attachment ID: {att.id}\n")
        f.write(f"  Remedy ID: {att.remedy.id}\n")
        f.write(f"  File: {att.file.name if att.file else 'No file'}\n")
        f.write(f"  File URL: {att.file_url}\n")
        f.write(f"  Type: {att.file_type}\n")
        f.write(f"  Purpose: {att.purpose}\n")
        f.write(f"  Issue ID: {att.remedy.issue.id}\n")
        f.write("\n")
    
    f.write("\n=== Direct Remedy Check ===\n")
    for remedy in Remedy.objects.all()[:5]:
        f.write(f"Remedy ID: {remedy.id}\n")
        f.write(f"  Issue: {remedy.issue.auto_title}\n")
        f.write(f"  Attachments count: {remedy.attachments.count()}\n")
        for att in remedy.attachments.all():
            f.write(f"    - {att.file_type} ({att.purpose}): {att.file_url}\n")
        f.write("\n")

print("Results written to attachment_check_results.txt")