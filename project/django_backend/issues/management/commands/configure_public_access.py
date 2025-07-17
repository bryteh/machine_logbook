from django.core.management.base import BaseCommand
from issues.models import Permission, PublicRole

class Command(BaseCommand):
    help = 'Configure public user access permissions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show current public permissions',
        )
        parser.add_argument(
            '--grant',
            type=str,
            help='Grant permission to public users (comma-separated list)',
        )
        parser.add_argument(
            '--revoke',
            type=str,
            help='Revoke permission from public users (comma-separated list)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset to default public permissions (crud_issues, crud_remedies)',
        )
    
    def handle(self, *args, **options):
        public_role = PublicRole.load()
        
        if options['show']:
            self.show_current_permissions(public_role)
        elif options['grant']:
            self.grant_permissions(public_role, options['grant'])
        elif options['revoke']:
            self.revoke_permissions(public_role, options['revoke'])
        elif options['reset']:
            self.reset_permissions(public_role)
        else:
            self.stdout.write(self.style.WARNING('No action specified. Use --help for options.'))
    
    def show_current_permissions(self, public_role):
        """Show current public permissions"""
        self.stdout.write(self.style.SUCCESS('Current Public User Permissions:'))
        self.stdout.write('=' * 40)
        
        current_perms = public_role.permissions.all()
        if current_perms:
            for perm in current_perms:
                self.stdout.write(f"✓ {perm.name} ({perm.codename})")
        else:
            self.stdout.write("No permissions granted to public users")
        
        self.stdout.write('\nAvailable Permissions:')
        self.stdout.write('-' * 20)
        all_perms = Permission.objects.all()
        for perm in all_perms:
            status = "✓" if perm in current_perms else "✗"
            self.stdout.write(f"{status} {perm.name} ({perm.codename})")
    
    def grant_permissions(self, public_role, permission_codenames):
        """Grant permissions to public users"""
        codenames = [name.strip() for name in permission_codenames.split(',')]
        granted = []
        
        for codename in codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                public_role.permissions.add(permission)
                granted.append(permission.name)
                self.stdout.write(f"✓ Granted: {permission.name}")
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Permission not found: {codename}"))
        
        if granted:
            self.stdout.write(self.style.SUCCESS(f"\nGranted {len(granted)} permissions to public users."))
    
    def revoke_permissions(self, public_role, permission_codenames):
        """Revoke permissions from public users"""
        codenames = [name.strip() for name in permission_codenames.split(',')]
        revoked = []
        
        for codename in codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                public_role.permissions.remove(permission)
                revoked.append(permission.name)
                self.stdout.write(f"✓ Revoked: {permission.name}")
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Permission not found: {codename}"))
        
        if revoked:
            self.stdout.write(self.style.SUCCESS(f"\nRevoked {len(revoked)} permissions from public users."))
    
    def reset_permissions(self, public_role):
        """Reset to default public permissions"""
        # Default permissions for public users
        default_permissions = ['crud_issues', 'crud_remedies']
        
        # Clear all current permissions
        public_role.permissions.clear()
        
        # Add default permissions
        for codename in default_permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                public_role.permissions.add(permission)
                self.stdout.write(f"✓ Added: {permission.name}")
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Default permission not found: {codename}"))
        
        self.stdout.write(self.style.SUCCESS(f"\nReset public permissions to defaults: {', '.join(default_permissions)}")) 