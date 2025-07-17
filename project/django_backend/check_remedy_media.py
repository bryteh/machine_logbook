#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

print("=== Checking Remedy Media Data ===")
print(f"Total issues: {Issue.objects.count()}")
print(f"Total remedies: {Remedy.objects.count()}")
print(f"Total attachments: {Attachment.objects.count()}")
print(f"Issue attachments: {Attachment.objects.filter(issue__isnull=False).count()}")
print(f"Remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")

print("\n=== Remedy Attachment Details ===")
for remedy in Remedy.objects.all()[:5]:
    attachments = remedy.attachments.all()
    print(f"\nRemedy {remedy.id}:")
    print(f"  Description: {remedy.description[:50]}...")
    print(f"  Attachments count: {attachments.count()}")
    
    for attachment in attachments:
        print(f"    - ID: {attachment.id}")
        print(f"      File: {attachment.file}")
        print(f"      File URL: {attachment.file_url}")
        print(f"      File Name: {attachment.file.name if attachment.file else 'None'}")
        print(f"      File Type: {attachment.file_type}")
        print(f"      Purpose: {attachment.purpose}")
        
        # Check if file actually exists
        if attachment.file:
            file_path = attachment.file.path
            exists = os.path.exists(file_path)
            print(f"      File exists on disk: {exists}")
            if exists:
                file_size = os.path.getsize(file_path)
                print(f"      File size: {file_size} bytes")

print("\n=== Sample Issue Attachment for Comparison ===")
for issue in Issue.objects.all()[:2]:
    attachments = issue.attachments.all()
    print(f"\nIssue {issue.id}:")
    print(f"  Attachments count: {attachments.count()}")
    
    for attachment in attachments:
        print(f"    - ID: {attachment.id}")
        print(f"      File: {attachment.file}")
        print(f"      File URL: {attachment.file_url}")
        print(f"      File Type: {attachment.file_type}")