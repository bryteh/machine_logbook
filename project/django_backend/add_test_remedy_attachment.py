#!/usr/bin/env python
import os
import sys
import django
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

def add_test_attachment():
    print("=== Adding Test Remedy Attachment ===")
    
    # Get the first remedy
    remedy = Remedy.objects.first()
    if not remedy:
        print("No remedies found in database")
        return
    
    print(f"Found remedy: {remedy.id}")
    print(f"Current attachments: {remedy.attachments.count()}")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    # Create attachment
    attachment = Attachment.objects.create(
        remedy=remedy,
        file_type='image',
        purpose='documentation'
    )
    
    # Save the file
    attachment.file.save(
        'test_remedy_image.png',
        ContentFile(img_io.getvalue()),
        save=True
    )
    
    print(f"Created attachment: {attachment.id}")
    print(f"File path: {attachment.file.name}")
    print(f"File URL: {attachment.file.url}")
    print(f"File exists: {attachment.file.storage.exists(attachment.file.name)}")
    
    # Verify the attachment is linked to remedy
    print(f"Remedy now has {remedy.attachments.count()} attachments")
    
    return attachment

if __name__ == '__main__':
    add_test_attachment()