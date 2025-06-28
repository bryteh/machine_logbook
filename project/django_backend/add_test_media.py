#!/usr/bin/env python
"""
Script to add test media attachments to existing issues for testing the media display functionality.
"""

import os
import sys
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64

# Setup Django environment
sys.path.append('/c%3A/Users/admin/OneDrive/Desktop/AI/erabase_erp/machine_maintenance_logbook/project/django_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

def create_test_image():
    """Create a simple test image file"""
    # Create a simple 1x1 pixel PNG image in base64
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU8'
        'OhQAAAABJRU5ErkJggg=='
    )
    return ContentFile(png_data, name='test_image.png')

def add_test_attachments():
    """Add test attachments to existing issues and remedies"""
    
    # Get the first issue
    issue = Issue.objects.first()
    if not issue:
        print("No issues found. Please create an issue first.")
        return
    
    print(f"Adding test attachments to issue: {issue.auto_title}")
    
    # Create test image attachment for issue
    test_image = create_test_image()
    attachment = Attachment.objects.create(
        issue=issue,
        file=test_image,
        file_type='image',
        purpose='alarm_screen'
    )
    print(f"Created issue attachment: {attachment.id}")
    
    # Get the first remedy of this issue if it exists
    remedy = issue.remedies.first()
    if remedy:
        print(f"Adding test attachment to remedy: {remedy.id}")
        
        # Create test image attachment for remedy
        test_image2 = create_test_image()
        remedy_attachment = Attachment.objects.create(
            remedy=remedy,
            file=test_image2,
            file_type='image',
            purpose='other'
        )
        print(f"Created remedy attachment: {remedy_attachment.id}")
    
    print("Test attachments created successfully!")
    print(f"Issue {issue.id} now has {issue.attachments.count()} attachments")
    if remedy:
        print(f"Remedy {remedy.id} now has {remedy.attachments.count()} attachments")

if __name__ == '__main__':
    add_test_attachments() 