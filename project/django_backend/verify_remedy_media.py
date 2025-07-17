#!/usr/bin/env python
import os
import sys
import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment
from issues.serializers import RemedySerializer

print("=== Verifying Remedy Media Setup ===")

# Check database counts
print(f"Total remedies: {Remedy.objects.count()}")
print(f"Total remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")

# Get first remedy and check its attachments
remedy = Remedy.objects.first()
if remedy:
    print(f"\nChecking Remedy {remedy.id}:")
    print(f"  Description: {remedy.description[:50]}...")
    
    # Check attachments count
    attachments_count = remedy.attachments.count()
    print(f"  Attachments count: {attachments_count}")
    
    if attachments_count == 0:
        print("  Creating test attachment...")
        
        # Create a simple text file
        file_content = f"Test file for remedy {remedy.id}\nThis is a test attachment."
        file_name = f"remedy_{remedy.id}_test.txt"
        file_path = f"remedy_attachments/{file_name}"
        
        # Save the file
        saved_path = default_storage.save(file_path, ContentFile(file_content.encode()))
        
        # Create attachment with correct file_type
        attachment = Attachment.objects.create(
            remedy=remedy,
            file=saved_path,
            file_type='image',  # Using 'image' as it's one of the valid choices
            purpose='other'
        )
        
        print(f"  Created attachment {attachment.id}")
        print(f"  File path: {saved_path}")
        print(f"  File URL: {attachment.file_url}")
    
    # Test serialization
    print("\n  Testing serialization:")
    serializer = RemedySerializer(remedy)
    serialized_data = serializer.data
    
    print(f"  Serialized attachments count: {len(serialized_data.get('attachments', []))}")
    
    for att_data in serialized_data.get('attachments', []):
        print(f"    - ID: {att_data['id']}")
        print(f"      File URL: {att_data['file_url']}")
        print(f"      File Name: {att_data['file_name']}")
        print(f"      File Type: {att_data['file_type']}")
        
        # Test if URL is accessible
        if att_data['file_url']:
            try:
                response = requests.get(f"http://127.0.0.1:8000{att_data['file_url']}", timeout=5)
                print(f"      URL accessible: {response.status_code == 200}")
            except Exception as e:
                print(f"      URL test failed: {e}")
else:
    print("No remedies found in database")

print("\n=== Summary ===")
print(f"Remedy attachments in DB: {Attachment.objects.filter(remedy__isnull=False).count()}")
print(f"Issue attachments in DB: {Attachment.objects.filter(issue__isnull=False).count()}")