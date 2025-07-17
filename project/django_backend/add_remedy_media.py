#!/usr/bin/env python
import os
import sys
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

print("Adding test remedy media...")

# Get the first few remedies
remedies = Remedy.objects.all()[:3]

for i, remedy in enumerate(remedies):
    print(f"\nProcessing Remedy {remedy.id}...")
    
    # Check if remedy already has attachments
    existing_attachments = remedy.attachments.count()
    print(f"  Existing attachments: {existing_attachments}")
    
    if existing_attachments == 0:
        # Create a simple text file as test media
        file_content = f"Test remedy media file for remedy {remedy.id}\nDescription: {remedy.description}\nCreated for testing media display."
        
        # Create the file
        file_name = f"remedy_{remedy.id}_test_media.txt"
        file_path = f"remedy_attachments/{file_name}"
        
        # Save the file
        saved_path = default_storage.save(file_path, ContentFile(file_content.encode()))
        
        # Create the attachment record
        attachment = Attachment.objects.create(
            remedy=remedy,
            file=saved_path,
            file_type='document',
            purpose='documentation'
        )
        
        print(f"  Created attachment: {attachment.id}")
        print(f"  File path: {saved_path}")
        print(f"  File URL: {attachment.file_url}")
    else:
        print(f"  Remedy already has {existing_attachments} attachments")

print("\n=== Final Summary ===")
print(f"Total remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")
print(f"Total issue attachments: {Attachment.objects.filter(issue__isnull=False).count()}")

# List all remedy attachments
print("\n=== All Remedy Attachments ===")
for attachment in Attachment.objects.filter(remedy__isnull=False):
    print(f"Remedy {attachment.remedy.id}: {attachment.file_name} ({attachment.file_type})")
    print(f"  URL: {attachment.file_url}")