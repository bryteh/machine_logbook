from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models, transaction
from issues.models import UserRole

class Command(BaseCommand):
    help = 'Clean up orphaned UserRole records and fix foreign key issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup of all issues',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("🔍 Checking for UserRole cleanup issues...")
        
        # Find orphaned UserRole records (UserRoles without valid Users)
        orphaned_user_roles = UserRole.objects.filter(user__isnull=True)
        orphaned_count = orphaned_user_roles.count()
        
        # Find UserRoles pointing to non-existent users
        invalid_user_roles = []
        for user_role in UserRole.objects.all():
            try:
                # Try to access the user
                _ = user_role.user.username
            except User.DoesNotExist:
                invalid_user_roles.append(user_role)
        
        # Find users that might have duplicate UserRoles
        duplicate_issues = []
        user_ids_with_multiple_roles = UserRole.objects.values('user_id').annotate(
            count=models.Count('user_id')
        ).filter(count__gt=1).values_list('user_id', flat=True)
        
        for user_id in user_ids_with_multiple_roles:
            user_roles = UserRole.objects.filter(user_id=user_id)
            duplicate_issues.append({
                'user_id': user_id,
                'roles': list(user_roles.values_list('id', 'role__name'))
            })
        
        # Report findings
        self.stdout.write(f"📊 Cleanup Analysis:")
        self.stdout.write(f"  - Orphaned UserRoles: {orphaned_count}")
        self.stdout.write(f"  - Invalid UserRoles: {len(invalid_user_roles)}")
        self.stdout.write(f"  - Users with duplicate roles: {len(duplicate_issues)}")
        
        if orphaned_count == 0 and len(invalid_user_roles) == 0 and len(duplicate_issues) == 0:
            self.stdout.write(self.style.SUCCESS("✅ No cleanup needed - everything looks good!"))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN - No changes will be made"))
            
            if orphaned_user_roles.exists():
                self.stdout.write("Would delete orphaned UserRoles:")
                for ur in orphaned_user_roles:
                    self.stdout.write(f"  - UserRole ID {ur.id}")
            
            if invalid_user_roles:
                self.stdout.write("Would delete invalid UserRoles:")
                for ur in invalid_user_roles:
                    self.stdout.write(f"  - UserRole ID {ur.id} (user_id: {ur.user_id})")
            
            if duplicate_issues:
                self.stdout.write("Would fix duplicate UserRoles:")
                for issue in duplicate_issues:
                    self.stdout.write(f"  - User ID {issue['user_id']}: {issue['roles']}")
            
            self.stdout.write("\nRun without --dry-run to apply fixes.")
            return
        
        if not force:
            response = input("⚠️  This will modify/delete UserRole records. Continue? (y/N): ")
            if response.lower() != 'y':
                self.stdout.write("Cancelled.")
                return
        
        # Perform cleanup
        with transaction.atomic():
            cleaned_count = 0
            
            # Clean up orphaned UserRoles
            if orphaned_user_roles.exists():
                count = orphaned_user_roles.count()
                orphaned_user_roles.delete()
                cleaned_count += count
                self.stdout.write(f"✓ Deleted {count} orphaned UserRoles")
            
            # Clean up invalid UserRoles
            if invalid_user_roles:
                for ur in invalid_user_roles:
                    ur.delete()
                    cleaned_count += 1
                self.stdout.write(f"✓ Deleted {len(invalid_user_roles)} invalid UserRoles")
            
            # Fix duplicate UserRoles (keep the most recent one)
            if duplicate_issues:
                for issue in duplicate_issues:
                    user_roles = UserRole.objects.filter(user_id=issue['user_id']).order_by('-created_at')
                    # Keep the first (most recent), delete the rest
                    to_delete = user_roles[1:]
                    for ur in to_delete:
                        ur.delete()
                        cleaned_count += 1
                self.stdout.write(f"✓ Fixed {len(duplicate_issues)} duplicate UserRole issues")
        
        self.stdout.write(self.style.SUCCESS(f"🎉 Cleanup complete! Processed {cleaned_count} records."))
        self.stdout.write("User deletion should now work properly in Django Admin.") 