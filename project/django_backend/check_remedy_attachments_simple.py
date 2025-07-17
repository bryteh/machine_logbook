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
from issues.serializers import IssueDetailSerializer
from django.contrib.auth.models import User
from rest_framework.request import Request
from django.test import RequestFactory

print("=== Database Check ===")
print(f"Total Issues: {Issue.objects.count()}")
print(f"Total Remedies: {Remedy.objects.count()}")
print(f"Total Attachments: {Attachment.objects.count()}")
print(f"Remedy Attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")
print(f"Issue Attachments: {Attachment.objects.filter(issue__isnull=False).count()}")

print("\n=== Remedy Attachment Details ===")
remedy_attachments = Attachment.objects.filter(remedy__isnull=False)
for att in remedy_attachments:
    print(f"Attachment ID: {att.id}")
    print(f"  Remedy ID: {att.remedy.id}")
    print(f"  File: {att.file.name if att.file else 'No file'}")
    print(f"  File URL: {att.file_url}")
    print(f"  Type: {att.file_type}")
    print(f"  Purpose: {att.purpose}")
    print(f"  Issue ID: {att.remedy.issue.id}")
    print()

print("\n=== API Serialization Test ===")
# Get the first issue with remedies
issue_with_remedies = Issue.objects.filter(remedies__isnull=False).first()
if issue_with_remedies:
    print(f"Testing Issue: {issue_with_remedies.id}")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/issues/')
    
    # Create a mock user (optional)
    try:
        user = User.objects.first()
        if user:
            request.user = user
    except:
        pass
    
    # Serialize the issue
    serializer = IssueDetailSerializer(issue_with_remedies, context={'request': request})
    data = serializer.data
    
    print(f"Remedies count in serialized data: {len(data.get('remedies', []))}")
    
    for i, remedy_data in enumerate(data.get('remedies', [])):
        print(f"\nRemedy {i+1}:")
        print(f"  ID: {remedy_data.get('id')}")
        print(f"  Description: {remedy_data.get('description', '')[:50]}...")
        print(f"  Attachments count: {len(remedy_data.get('attachments', []))}")
        
        for j, att_data in enumerate(remedy_data.get('attachments', [])):
            print(f"    Attachment {j+1}:")
            print(f"      ID: {att_data.get('id')}")
            print(f"      File URL: {att_data.get('file_url')}")
            print(f"      File Name: {att_data.get('file_name')}")
            print(f"      Type: {att_data.get('file_type')}")
            print(f"      Purpose: {att_data.get('purpose')}")
else:
    print("No issues with remedies found")

print("\n=== Direct Remedy Check ===")
for remedy in Remedy.objects.all()[:3]:
    print(f"Remedy ID: {remedy.id}")
    print(f"  Issue: {remedy.issue.auto_title}")
    print(f"  Attachments count: {remedy.attachments.count()}")
    for att in remedy.attachments.all():
        print(f"    - {att.file_type} ({att.purpose}): {att.file_url}")
    print()

print("Done!")