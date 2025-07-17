#!/usr/bin/env python
"""
Comprehensive test script for all three issues
"""
import os
import sys
import django
import requests
import json

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from issues.models import UserRole, Role, PublicRole, Issue
from django.db import transaction

BASE_URL = "http://127.0.0.1:8000"

def test_public_remedy_creation():
    """Test Issue 1: Public remedy creation"""
    print("🧪 Testing Public Remedy Creation")
    print("=" * 40)
    
    try:
        # First, create a test issue to add remedy to
        issue_data = {
            "category": "mechanical",
            "priority": "medium",
            "machine_id_ref": "TEST001",
            "description": "Test issue for remedy creation",
            "reported_by": "Test User"
        }
        
        # Create issue via API (should work for public users)
        response = requests.post(f"{BASE_URL}/api/issues/", json=issue_data)
        if response.status_code != 201:
            print(f"❌ Failed to create test issue: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        issue_id = response.json()['id']
        print(f"✓ Created test issue: {issue_id}")
        
        # Now try to create a remedy as public user
        remedy_data = {
            "description": "Test remedy from public user",
            "technician_name": "External Tech",
            "is_external": True,
            "phone_number": "123-456-7890",
            "is_machine_runnable": True
        }
        
        response = requests.post(f"{BASE_URL}/api/issues/{issue_id}/remedies/", json=remedy_data)
        
        if response.status_code == 201:
            print("✅ SUCCESS: Public remedy creation works!")
            remedy_id = response.json()['id']
            print(f"   Created remedy: {remedy_id}")
            
            # Clean up
            try:
                Issue.objects.get(id=issue_id).delete()
                print("✓ Cleaned up test data")
            except:
                pass
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_user_deletion():
    """Test Issue 2: User deletion"""
    print("\n🧪 Testing User Deletion")
    print("=" * 30)
    
    try:
        # Create a test user
        user = User.objects.create_user(
            username="test_delete_user_2", 
            email="test2@example.com",
            password="testpass123"
        )
        print(f"✓ Created test user: {user.username}")
        
        # Assign a role
        try:
            admin_role = Role.objects.get(codename='admin')
            user_role = UserRole.objects.create(user=user, role=admin_role)
            print(f"✓ Assigned role: {admin_role.name}")
        except Role.DoesNotExist:
            print("❌ Admin role not found")
            user_role = None
        
        # Test deletion
        user_id = user.id
        user.delete()
        
        # Check if UserRole was cleaned up
        remaining_roles = UserRole.objects.filter(user_id=user_id).count()
        
        if remaining_roles == 0:
            print("✅ SUCCESS: User deletion works correctly!")
            print("   UserRole was properly cleaned up")
            return True
        else:
            print(f"❌ FAILED: {remaining_roles} UserRole records still exist")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_login_functionality():
    """Test Issue 3: Login functionality"""
    print("\n🧪 Testing Login Functionality")
    print("=" * 35)
    
    try:
        # Create a test user for login
        test_username = "test_login_user"
        test_password = "testpass123"
        
        # Clean up any existing user
        try:
            User.objects.get(username=test_username).delete()
        except User.DoesNotExist:
            pass
        
        user = User.objects.create_user(
            username=test_username,
            email="login@example.com", 
            password=test_password
        )
        print(f"✓ Created test login user: {user.username}")
        
        # Assign a role
        try:
            admin_role = Role.objects.get(codename='admin')
            UserRole.objects.create(user=user, role=admin_role)
            print(f"✓ Assigned role: {admin_role.name}")
        except Role.DoesNotExist:
            print("⚠️  Admin role not found, continuing without role")
        
        # Test login via API
        login_data = {
            "username": test_username,
            "password": test_password
        }
        
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Login works correctly!")
            response_data = response.json()
            print(f"   Message: {response_data.get('message')}")
            if 'user' in response_data:
                print(f"   Username: {response_data['user']['username']}")
                if response_data['user']['role']:
                    print(f"   Role: {response_data['user']['role']['role_name']}")
            
            # Test authenticated endpoint
            current_user_response = session.get(f"{BASE_URL}/api/auth/current-user/")
            if current_user_response.status_code == 200:
                print("✓ Authenticated endpoint access works")
            else:
                print(f"⚠️  Authenticated endpoint failed: {current_user_response.status_code}")
            
            # Clean up
            try:
                user.delete()
                print("✓ Cleaned up test user")
            except:
                pass
            
            return True
        else:
            print(f"❌ FAILED: Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
            # Clean up
            try:
                user.delete()
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_public_permissions():
    """Test public permission configuration"""
    print("\n🧪 Testing Public Permission Configuration")
    print("=" * 45)
    
    try:
        public_role = PublicRole.load()
        print(f"✓ Loaded public role")
        
        current_perms = list(public_role.permissions.values_list('codename', flat=True))
        print(f"✓ Current public permissions: {current_perms}")
        
        # Test that crud_remedies is enabled for public
        if 'crud_remedies' in current_perms:
            print("✅ SUCCESS: Public users can create remedies (permission set)")
            return True
        else:
            print("❌ FAILED: crud_remedies not in public permissions")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_all_issues():
    print("Testing all three issues...")
    
    # Test 1: Public permissions
    try:
        public_role = PublicRole.load()
        perms = list(public_role.permissions.values_list('codename', flat=True))
        print(f"✓ Public permissions: {perms}")
        if 'crud_remedies' in perms:
            print("✅ Public can create remedies")
        else:
            print("❌ Public cannot create remedies")
    except Exception as e:
        print(f"❌ Public role error: {e}")
    
    # Test 2: User deletion
    try:
        user = User.objects.create_user(username="test_del", password="test123")
        try:
            admin_role = Role.objects.get(codename='admin')
            UserRole.objects.create(user=user, role=admin_role)
        except:
            pass
        
        user_id = user.id
        user.delete()
        
        remaining = UserRole.objects.filter(user_id=user_id).count()
        if remaining == 0:
            print("✅ User deletion works")
        else:
            print(f"❌ User deletion failed, {remaining} roles remain")
    except Exception as e:
        print(f"❌ User deletion error: {e}")
    
    # Test 3: Login view
    try:
        from issues.views import LoginView
        print("✅ Login view is importable")
    except Exception as e:
        print(f"❌ Login view error: {e}")
    
    print("Test complete!")

def main():
    """Run all tests"""
    print("🚀 Testing All Three Issues - Comprehensive Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print("✓ Django server is running")
    except requests.ConnectionError:
        print("❌ Django server is not running. Please start it with 'python manage.py runserver'")
        return
    
    # Run tests
    test1_result = test_public_remedy_creation()
    test2_result = test_user_deletion() 
    test3_result = test_login_functionality()
    test4_result = test_public_permissions()
    
    print("\n" + "=" * 60)
    print("📋 Comprehensive Test Results:")
    print(f"  1. Public Remedy Creation: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  2. User Deletion: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"  3. Login Functionality: {'✅ PASS' if test3_result else '❌ FAIL'}")
    print(f"  4. Public Permissions: {'✅ PASS' if test4_result else '❌ FAIL'}")
    
    all_passed = test1_result and test2_result and test3_result and test4_result
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! All three issues are fixed.")
        print("\n✅ You can now:")
        print("  1. Create remedies as public users without authentication errors")
        print("  2. Delete users in Django Admin without foreign key errors") 
        print("  3. Login successfully with proper user data returned")
        print("  4. Configure public permissions in Django Admin")
    else:
        print("\n⚠️  Some tests failed. Check the specific error messages above.")
        print("\n🔧 Next steps:")
        if not test1_result:
            print("  - Check public remedy creation permissions and API endpoints")
        if not test2_result:
            print("  - Check user deletion cascade configuration")
        if not test3_result:
            print("  - Check login endpoint and session handling")
        if not test4_result:
            print("  - Check public role permissions configuration")

if __name__ == "__main__":
    test_all_issues() 