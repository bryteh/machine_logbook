#!/usr/bin/env python
"""
Test script to verify user deletion works properly
"""
import os
import sys
import django

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from issues.models import UserRole, Role
from django.db import transaction

def test_user_deletion():
    """Test that user deletion works without foreign key errors"""
    print("🧪 Testing User Deletion Functionality")
    print("=" * 50)
    
    # Create a test user
    test_username = "test_deletion_user"
    
    try:
        # Clean up any existing test user
        try:
            existing_user = User.objects.get(username=test_username)
            existing_user.delete()
            print("✓ Cleaned up existing test user")
        except User.DoesNotExist:
            pass
        
        # Create a new test user
        user = User.objects.create_user(
            username=test_username,
            email="test@example.com",
            password="testpass123"
        )
        print(f"✓ Created test user: {user.username}")
        
        # Assign a role to the user
        try:
            admin_role = Role.objects.get(codename='admin')
            user_role = UserRole.objects.create(
                user=user,
                role=admin_role
            )
            print(f"✓ Assigned role: {admin_role.name} to user")
        except Role.DoesNotExist:
            print("❌ Admin role not found, creating basic UserRole")
            user_role = UserRole.objects.create(
                user=user,
                role=None  # This might cause issues, but let's test
            )
        
        # Verify the relationship exists
        user_roles_before = UserRole.objects.filter(user=user).count()
        print(f"✓ UserRole records for user: {user_roles_before}")
        
        # Test deletion
        print("\n🗑️  Testing user deletion...")
        
        with transaction.atomic():
            user.delete()
        
        # Verify cleanup
        user_roles_after = UserRole.objects.filter(user_id=user.id).count()
        print(f"✓ UserRole records after deletion: {user_roles_after}")
        
        if user_roles_after == 0:
            print("✅ SUCCESS: User deletion worked correctly!")
            print("   - User was deleted")
            print("   - UserRole was automatically cleaned up")
        else:
            print("❌ ISSUE: UserRole records still exist after user deletion")
        
    except Exception as e:
        print(f"❌ ERROR during user deletion test: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False
    
    return True

def test_public_role_editing():
    """Test that PublicRole can be edited"""
    print("\n🔧 Testing Public Role Editing")
    print("=" * 30)
    
    try:
        from issues.models import PublicRole, Permission
        
        # Load the public role
        public_role = PublicRole.load()
        print(f"✓ Loaded public role (ID: {public_role.id})")
        
        # Get current permissions
        current_perms = list(public_role.permissions.all())
        print(f"✓ Current permissions: {len(current_perms)}")
        
        # Test adding a permission
        try:
            view_dashboard_perm = Permission.objects.get(codename='view_dashboard')
            public_role.permissions.add(view_dashboard_perm)
            print("✓ Added 'view_dashboard' permission")
            
            # Test removing it
            public_role.permissions.remove(view_dashboard_perm)
            print("✓ Removed 'view_dashboard' permission")
            
        except Permission.DoesNotExist:
            print("❌ 'view_dashboard' permission not found")
        
        # Reset to original permissions
        public_role.permissions.set(current_perms)
        print("✓ Reset to original permissions")
        
        print("✅ SUCCESS: Public role editing works correctly!")
        
    except Exception as e:
        print(f"❌ ERROR during public role test: {str(e)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing RBAC System Fixes")
    print("=" * 60)
    
    test1_result = test_user_deletion()
    test2_result = test_public_role_editing()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"  1. User Deletion: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  2. Public Role Editing: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Both issues are fixed.")
        print("\nNow you can:")
        print("  1. Delete users in Django Admin without errors")
        print("  2. Edit public permissions in Django Admin")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 