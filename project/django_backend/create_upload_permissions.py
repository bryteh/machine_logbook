#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Permission, PublicRole

def add_upload_permissions_to_public_role():
    """
    Add media upload permissions to the public role:
    - upload_media_attachments (general media upload)
    - upload_issue_media (issue-specific media)
    - upload_remedy_media (remedy-specific media)
    """
    print("Adding media upload permissions to public role...")
    
    # Get or create the public role
    public_role = PublicRole.load()
    
    # Define required permissions
    required_permissions = [
        {
            'name': 'Upload Media Attachments',
            'codename': 'upload_media_attachments',
            'description': 'Can upload media attachments',
            'category': 'media'
        },
        {
            'name': 'Upload Issue Media',
            'codename': 'upload_issue_media',
            'description': 'Can upload media for issues',
            'category': 'media'
        },
        {
            'name': 'Upload Remedy Media',
            'codename': 'upload_remedy_media',
            'description': 'Can upload media for remedies',
            'category': 'media'
        }
    ]
    
    # Create permissions if they don't exist
    for perm_data in required_permissions:
        perm, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            defaults={
                'name': perm_data['name'],
                'description': perm_data['description'],
                'category': perm_data['category']
            }
        )
        
        if created:
            print(f"Created permission: {perm.name}")
        
        # Add permission to public role if not already added
        if perm not in public_role.permissions.all():
            public_role.permissions.add(perm)
            print(f"Added permission '{perm.name}' to public role")
        else:
            print(f"Permission '{perm.name}' already in public role")
    
    print("Public role now has the following permissions:")
    for perm in public_role.permissions.all():
        print(f"- {perm.name} ({perm.codename})")

if __name__ == "__main__":
    add_upload_permissions_to_public_role()
    print("Done!") 