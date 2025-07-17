from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from issues.models import UserRole


class Command(BaseCommand):
    help = 'Create demo users with different roles for testing'

    def handle(self, *args, **options):
        # Create demo users
        users_data = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@factory.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'can_view_costs': True,
                'can_view_external_contacts': True,
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'manager',
                'password': 'manager123',
                'email': 'manager@factory.com',
                'first_name': 'Factory',
                'last_name': 'Manager',
                'role': 'manager',
                'can_view_costs': True,
                'can_view_external_contacts': True,
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'technician',
                'password': 'tech123',
                'email': 'tech@factory.com',
                'first_name': 'John',
                'last_name': 'Technician',
                'role': 'technician',
                'can_view_costs': False,
                'can_view_external_contacts': False,
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'viewer',
                'password': 'viewer123',
                'email': 'viewer@factory.com',
                'first_name': 'Read',
                'last_name': 'Only',
                'role': 'viewer',
                'can_view_costs': False,
                'can_view_external_contacts': False,
                'is_staff': False,
                'is_superuser': False
            }
        ]

        for user_data in users_data:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists - skipping')
                )
                continue
            
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser']
            )
            
            # Create user role
            UserRole.objects.create(
                user=user,
                role=user_data['role'],
                can_view_costs=user_data['can_view_costs'],
                can_view_external_contacts=user_data['can_view_external_contacts']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {username} with role: {user_data["role"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Demo Users Created ===')
        )
        self.stdout.write('Login credentials:')
        for user_data in users_data:
            self.stdout.write(f'  {user_data["role"].title()}: {user_data["username"]} / {user_data["password"]}')
        
        self.stdout.write('\nAccess levels:')
        self.stdout.write('  Admin: Full access, can view costs and external contacts')
        self.stdout.write('  Manager: Full access, can view costs and external contacts')
        self.stdout.write('  Technician: Limited access, cannot view costs or external contacts')
        self.stdout.write('  Viewer: Read-only access')
        
        self.stdout.write('\nTo login, visit: http://127.0.0.1:8000/admin/') 