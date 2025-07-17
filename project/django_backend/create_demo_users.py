#!/usr/bin/env python
"""
Create demo users with different roles for testing
Run this from the django_backend directory with: python create_demo_users.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.contrib.auth.models import User
from issues.models import UserRole


def create_demo_users():
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

    print("Creating demo users...")
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f'⚠️  User {username} already exists - skipping')
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
        
        print(f'✅ Created user: {username} with role: {user_data["role"]}')
    
    print('\n=== Demo Users Created ===')
    print('Login credentials:')
    for user_data in users_data:
        print(f'  {user_data["role"].title()}: {user_data["username"]} / {user_data["password"]}')
    
    print('\nAccess levels:')
    print('  Admin: Full access, can view costs and external contacts')
    print('  Manager: Full access, can view costs and external contacts')
    print('  Technician: Limited access, cannot view costs or external contacts')
    print('  Viewer: Read-only access')
    
    print('\nTo test different permissions:')
    print('1. Visit: http://127.0.0.1:8000/admin/')
    print('2. Login with different users to see permission differences')
    print('3. Cost information will be hidden for technician/viewer roles')
    print('4. External contact info will be masked for technician/viewer roles')


if __name__ == '__main__':
    create_demo_users() 