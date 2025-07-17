#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.contrib.auth.models import User
from issues.models import UserRole

def check_admin_permissions():
    """Check admin user permissions"""
    
    print("🔍 CHECKING ADMIN USER PERMISSIONS")
    print("=" * 50)
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Found admin user: {admin_user.username}")
        print(f"   Is superuser: {admin_user.is_superuser}")
        print(f"   Is staff: {admin_user.is_staff}")
        
        # Check if user has a role
        try:
            user_role = UserRole.objects.get(user=admin_user)
            print(f"✅ Found user role: {user_role.role}")
            print(f"   Role name: {user_role.role.name}")
            
            # Get permissions
            permissions = user_role.get_all_permissions()
            print(f"\n📋 User permissions ({len(permissions)} total):")
            for perm in sorted(permissions):
                print(f"   • {perm}")
            
            # Check specific permission
            has_view_dashboard = 'view_dashboard' in permissions
            print(f"\n🎯 Has 'view_dashboard' permission: {has_view_dashboard}")
            
            if not has_view_dashboard:
                print("\n⚠️  ISSUE FOUND: Admin user does not have 'view_dashboard' permission!")
                print("   This explains why the dashboard is causing redirect loops.")
                
                # Check what permissions are available
                from issues.models import Permission
                all_perms = Permission.objects.all().values_list('codename', flat=True)
                dashboard_perms = [p for p in all_perms if 'dashboard' in p.lower()]
                print(f"\n📝 Available dashboard-related permissions:")
                for perm in dashboard_perms:
                    print(f"   • {perm}")
            
        except UserRole.DoesNotExist:
            print("❌ No user role found for admin user")
            print("   Admin user is superuser, so should have all permissions implicitly")
            
    except User.DoesNotExist:
        print("❌ Admin user not found")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    check_admin_permissions() 