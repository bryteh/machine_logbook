import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Remedy, Attachment, Issue

print(f"Total issues: {Issue.objects.count()}")
print(f"Total remedies: {Remedy.objects.count()}")
print(f"Total attachments: {Attachment.objects.count()}")
print(f"Remedy attachments: {Attachment.objects.filter(remedy__isnull=False).count()}")
print(f"Issue attachments: {Attachment.objects.filter(issue__isnull=False).count()}")

print("\n--- Remedy Details ---")
for remedy in Remedy.objects.all()[:5]:
    attachments = remedy.attachments.all()
    print(f"Remedy {remedy.id}: {attachments.count()} attachments")
    print(f"  Description: {remedy.description[:50]}...")
    print(f"  Labor cost: ${remedy.labor_cost}")
    print(f"  Parts cost: ${remedy.parts_cost}")
    print(f"  Total cost: ${remedy.total_cost}")
    
    for attachment in attachments:
        print(f"    - {attachment.file_name} ({attachment.file_type})")
        print(f"      URL: {attachment.file_url}")
        print(f"      Purpose: {attachment.purpose}")

print("\n--- Creating test remedy attachment ---")
if Remedy.objects.exists():
    remedy = Remedy.objects.first()
    # Check if attachment already exists
    if not remedy.attachments.exists():
        attachment = Attachment.objects.create(
            remedy=remedy,
            file='test_remedy_image.jpg',
            file_type='image',
            purpose='remedy'
        )
        print(f"Created test attachment: {attachment.file_name}")
    else:
        print("Remedy already has attachments")
else:
    print("No remedies found to attach to")