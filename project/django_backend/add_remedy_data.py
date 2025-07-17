import os
import django
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Remedy, Attachment

print("Adding remedy attachments and costs...")

# Get all remedies
remedies = Remedy.objects.all()
print(f"Found {remedies.count()} remedies")

for remedy in remedies:
    print(f"\nProcessing Remedy {remedy.id}:")
    print(f"  Description: {remedy.description[:50]}...")
    print(f"  Current attachments: {remedy.attachments.count()}")
    
    # Add attachment if none exists
    if remedy.attachments.count() == 0:
        try:
            # Create a simple text file as attachment
            file_content = ContentFile(b'Test remedy attachment content', name=f'remedy_{remedy.id}_document.txt')
            
            attachment = Attachment.objects.create(
                remedy=remedy,
                file=file_content,
                file_type='document',
                purpose='remedy'
            )
            print(f"  ✓ Created attachment: {attachment.file_name}")
        except Exception as e:
            print(f"  ✗ Error creating attachment: {e}")
    
    # Update costs if they're zero
    if remedy.labor_cost == 0 and remedy.parts_cost == 0:
        remedy.labor_cost = 120.00
        remedy.parts_cost = 85.50
        remedy.save()
        print(f"  ✓ Updated costs: Labor=${remedy.labor_cost}, Parts=${remedy.parts_cost}, Total=${remedy.total_cost}")
    else:
        print(f"  Current costs: Labor=${remedy.labor_cost}, Parts=${remedy.parts_cost}, Total=${remedy.total_cost}")

print(f"\nFinal count - Remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")
print("Done!")