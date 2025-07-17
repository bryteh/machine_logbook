from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from issues.models import Permission, Role, UserRole, PublicRole, GlobalSettings

class Command(BaseCommand):
    help = 'Setup initial RBAC system with default roles and permissions'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up RBAC system...')
        
        # Create all permissions
        permissions = [
            ('view_dashboard', 'View Dashboard', 'dashboard'),
            ('crud_issues', 'Create/Read/Update/Delete Issues', 'issues'),
            ('crud_remedies', 'Create/Read/Update/Delete Remedies', 'remedies'),
            ('mark_resolved', 'Mark Issues as Resolved', 'issues'),
            ('configure_limits', 'Configure System Limits', 'settings'),
            ('manage_users', 'Manage User Roles', 'users'),
            ('view_costs', 'View Cost Information', 'data'),
            ('view_external_contacts', 'View External Contact Info', 'data'),
            ('view_external_technician_names', 'View External Technician Names', 'data'),
            ('generate_reports', 'Generate PDF Reports', 'reports'),
        ]
        
        created_permissions = {}
        for codename, name, category in permissions:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name, 
                    'category': category,
                    'description': f'Allows user to {name.lower()}'
                }
            )
            created_permissions[codename] = perm
            if created:
                self.stdout.write(f"✓ Created permission: {name}")
            else:
                self.stdout.write(f"  Permission already exists: {name}")
        
        # Create roles with permission assignments
        role_configs = {
            'admin': {
                'name': 'Administrator',
                'description': 'Full system access with all permissions',
                'permissions': ['view_dashboard', 'crud_issues', 'crud_remedies', 'mark_resolved', 'configure_limits', 'manage_users', 'view_costs', 'view_external_contacts', 'view_external_technician_names', 'generate_reports']
            },
            'management': {
                'name': 'Management',
                'description': 'Management level access with all operational permissions',
                'permissions': ['view_dashboard', 'crud_issues', 'crud_remedies', 'mark_resolved', 'configure_limits', 'manage_users', 'view_costs', 'view_external_contacts', 'view_external_technician_names', 'generate_reports']
            },
            'executive': {
                'name': 'Executive',
                'description': 'Executive level access without system configuration',
                'permissions': ['view_dashboard', 'crud_issues', 'crud_remedies', 'mark_resolved', 'view_costs', 'view_external_contacts', 'view_external_technician_names', 'generate_reports']
            },
            'technician': {
                'name': 'Technician',
                'description': 'Technician access without resolution marking',
                'permissions': ['view_dashboard', 'crud_issues', 'crud_remedies', 'view_costs', 'view_external_contacts', 'view_external_technician_names']
            },
            'operator': {
                'name': 'Operator',
                'description': 'Basic operator access for issue reporting only',
                'permissions': ['crud_issues']
            },
        }
        
        for codename, config in role_configs.items():
            role, created = Role.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': config['name'],
                    'description': config['description']
                }
            )
            
            # Assign permissions
            role_permissions = [created_permissions[p] for p in config['permissions']]
            role.permissions.set(role_permissions)
            
            if created:
                self.stdout.write(f"✓ Created role: {config['name']} with {len(config['permissions'])} permissions")
            else:
                self.stdout.write(f"  Role already exists: {config['name']}, updating permissions")
                role.permissions.set(role_permissions)
        
        # Setup public permissions (what unauthenticated users can do)
        public_role = PublicRole.load()
        public_permissions = [
            created_permissions['crud_issues'],
            created_permissions['crud_remedies']
        ]
        public_role.permissions.set(public_permissions)
        self.stdout.write("✓ Configured public access permissions (crud_issues, crud_remedies)")
        
        # Create default global settings
        settings = GlobalSettings.load()
        self.stdout.write("✓ Created default global settings")
        
        # Migrate existing users if any
        existing_user_roles = UserRole.objects.all()
        migrated_count = 0
        for user_role in existing_user_roles:
            if hasattr(user_role, 'role') and isinstance(user_role.role, str):
                # This is old format, need to migrate
                old_role = user_role.role
                role_mapping = {
                    'admin': 'admin',
                    'manager': 'management',
                    'technician': 'technician',
                    'viewer': 'operator'
                }
                
                new_role_codename = role_mapping.get(old_role, 'operator')
                try:
                    new_role = Role.objects.get(codename=new_role_codename)
                    user_role.role = new_role
                    user_role.save()
                    migrated_count += 1
                    self.stdout.write(f"  Migrated user {user_role.user.username} from {old_role} to {new_role_codename}")
                except Role.DoesNotExist:
                    self.stdout.write(f"  Warning: Could not migrate user {user_role.user.username}, role {new_role_codename} not found")
        
        if migrated_count > 0:
            self.stdout.write(f"✓ Migrated {migrated_count} existing users to new role system")
        
        self.stdout.write(self.style.SUCCESS('\n🎉 RBAC system setup complete!'))
        self.stdout.write(self.style.SUCCESS('You can now manage roles and permissions through the admin interface or API.')) 