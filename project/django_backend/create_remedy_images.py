#!/usr/bin/env python
import os
import sys
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

print("Creating test images for remedy media...")

# Simple 1x1 pixel PNG image in base64
small_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
png_data = base64.b64decode(small_png_base64)

# Get the first few remedies
remedies = Remedy.objects.all()[:3]

for i, remedy in enumerate(remedies):
    print(f"\nProcessing Remedy {remedy.id}...")
    
    # Clear existing attachments first
    existing_count = remedy.attachments.count()
    if existing_count > 0:
        print(f"  Removing {existing_count} existing attachments...")
        remedy.attachments.all().delete()
    
    # Create a test image
    file_name = f"remedy_{remedy.id}_test_image.png"
    file_path = f"remedy_attachments/{file_name}"
    
    # Save the image file
    saved_path = default_storage.save(file_path, ContentFile(png_data))
    
    # Create the attachment record
    attachment = Attachment.objects.create(
        remedy=remedy,
        file=saved_path,
        file_type='image',
        purpose='other'
    )
    
    print(f"  Created image attachment: {attachment.id}")
    print(f"  File path: {saved_path}")
    print(f"  File URL: {attachment.file_url}")
    
    # Verify file exists
    if attachment.file:
        try:
            file_path = attachment.file.path
            exists = os.path.exists(file_path)
            print(f"  File exists on disk: {exists}")
            if exists:
                file_size = os.path.getsize(file_path)
                print(f"  File size: {file_size} bytes")
        except Exception as e:
            print(f"  Error checking file: {e}")

print("\n=== Final Summary ===")
print(f"Total remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")
print(f"Total issue attachments: {Attachment.objects.filter(issue__isnull=False).count()}")

# List all remedy attachments with their URLs
print("\n=== All Remedy Attachments ===")
for attachment in Attachment.objects.filter(remedy__isnull=False):
    print(f"Remedy {attachment.remedy.id}: {attachment.file.name} ({attachment.file_type})")
    print(f"  URL: {attachment.file_url}")