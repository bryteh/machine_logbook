#!/usr/bin/env python
import os
import sys
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy, Attachment

print("Creating test image for remedy media...")

# Create a simple test image
img = Image.new('RGB', (300, 200), color='lightblue')

# Add some text to the image (if PIL supports it)
try:
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    # Use default font
    draw.text((50, 80), "Test Remedy Image", fill='black')
    draw.text((50, 100), "Media Display Test", fill='black')
except:
    print("Could not add text to image, but image will still be created")

# Save image to bytes
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Get the first remedy
remedy = Remedy.objects.first()
if remedy:
    print(f"Adding test image to Remedy {remedy.id}")
    
    # Create the file
    file_name = f"remedy_{remedy.id}_test_image.png"
    file_path = f"remedy_attachments/{file_name}"
    
    # Save the file
    saved_path = default_storage.save(file_path, ContentFile(img_bytes.getvalue()))
    
    # Create the attachment record
    attachment = Attachment.objects.create(
        remedy=remedy,
        file=saved_path,
        file_type='image',
        purpose='documentation'
    )
    
    print(f"Created image attachment: {attachment.id}")
    print(f"File path: {saved_path}")
    print(f"File URL: {attachment.file_url}")
    
    # Verify file exists
    if attachment.file:
        file_path = attachment.file.path
        exists = os.path.exists(file_path)
        print(f"File exists on disk: {exists}")
        if exists:
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size} bytes")
else:
    print("No remedies found in database")

print("\n=== Current Remedy Attachments ===")
for attachment in Attachment.objects.filter(remedy__isnull=False):
    print(f"Remedy {attachment.remedy.id}: {attachment.file_name} ({attachment.file_type})")
    print(f"  URL: {attachment.file_url}")