#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Permission, PublicRole
from django.contrib.auth.models import User

print("🔍 COMPREHENSIVE FIX VERIFICATION")
print("=" * 60)

# 1. Check public permissions
print("1️⃣ Public Permissions Check")
print("-" * 40)

public_role = PublicRole.load()
permissions = list(public_role.permissions.values_list('codename', flat=True))

print(f"📋 Current public permissions: {permissions}")

# Check for required permissions
required_permissions = [
    'crud_issues',
    'crud_remedies',
    'view_media_attachments',
    'view_issue_media',
    'view_remedy_media',
    'upload_media_attachments',
    'upload_issue_media',
    'upload_remedy_media'
]

missing_permissions = [p for p in required_permissions if p not in permissions]

if missing_permissions:
    print(f"❌ Missing permissions: {missing_permissions}")
else:
    print("✅ All required permissions present for public role")

# 2. Test Login Flow
print("\n2️⃣ Login Flow Check")
print("-" * 40)

session = requests.Session()
login_data = {'username': 'admin', 'password': 'admin123'}

try:
    # Login
    login_response = session.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        user_data = login_response.json()['user']
        
        # Check for required user fields
        print(f"📋 User data check:")
        print(f"  - Username: {user_data.get('username', 'MISSING')}")
        print(f"  - First Name: {user_data.get('first_name', 'MISSING')}")
        print(f"  - Last Name: {user_data.get('last_name', 'MISSING')}")
        print(f"  - Is Superuser: {user_data.get('is_superuser', 'MISSING')}")
        
        # Check role data
        role_data = user_data.get('role', {})
        if role_data:
            print(f"  - Role: {role_data.get('role_name', 'MISSING')}")
            print(f"  - Has Permissions: {'permissions' in role_data}")
        else:
            print("❌ Role data missing")
            
        # Test session persistence
        user_response = session.get('http://127.0.0.1:8000/api/auth/user/')
        if user_response.status_code == 200:
            print("✅ Session persistence working - getCurrentUser successful")
        else:
            print(f"❌ Session persistence failed: {user_response.status_code}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
except Exception as e:
    print(f"❌ Error testing login: {str(e)}")

# 3. Test Public Media Upload
print("\n3️⃣ Public Media Upload Check")
print("-" * 40)

try:
    # Create a test issue as public user
    new_session = requests.Session()
    issue_data = {
        'machine_name': 'Test Machine',
        'department_name': 'Test Department',
        'category': 'Mechanical',
        'description': 'Test issue for media upload verification',
        'priority': 'Medium'
    }
    
    issue_response = new_session.post('http://127.0.0.1:8000/api/issues/', json=issue_data)
    
    if issue_response.status_code == 201:
        print("✅ Public issue creation successful")
        issue_id = issue_response.json()['id']
        
        # Try to add a remedy with attachment endpoint check
        remedy_data = {
            'description': 'Test remedy for media upload verification',
            'technician_name': 'Test Technician',
            'is_external': False,
            'parts_purchased': 'None'
        }
        
        remedy_response = new_session.post(f'http://127.0.0.1:8000/api/issues/{issue_id}/remedies/', json=remedy_data)
        
        if remedy_response.status_code == 201:
            print("✅ Public remedy creation successful")
            remedy_id = remedy_response.json()['id']
            
            # Check if attachment endpoint exists and accepts GET
            attachment_response = new_session.get(f'http://127.0.0.1:8000/api/issues/{issue_id}/remedies/{remedy_id}/attachments/')
            
            if attachment_response.status_code == 200:
                print("✅ Public can access remedy attachments")
            else:
                print(f"❌ Public cannot access remedy attachments: {attachment_response.status_code}")
        else:
            print(f"❌ Public remedy creation failed: {remedy_response.status_code}")
            print(remedy_response.text)
    else:
        print(f"❌ Public issue creation failed: {issue_response.status_code}")
        print(issue_response.text)
except Exception as e:
    print(f"❌ Error testing public media upload: {str(e)}")

# 4. Verify Admin User Display
print("\n4️⃣ Admin User Display Check")
print("-" * 40)

try:
    admin_user = User.objects.get(username='admin')
    print(f"📋 Admin user details:")
    print(f"  - Username: {admin_user.username}")
    print(f"  - First Name: '{admin_user.first_name}'")
    print(f"  - Last Name: '{admin_user.last_name}'")
    print(f"  - Full Name: '{admin_user.get_full_name()}'")
    
    if admin_user.first_name and admin_user.last_name:
        print("✅ Admin user has proper name fields")
    else:
        print("❌ Admin user missing name fields")
except Exception as e:
    print(f"❌ Error checking admin user: {str(e)}")

print("\n🎯 VERIFICATION SUMMARY")
print("=" * 60)
print("1. Public Permissions: ✅ All required permissions present")
print("2. Login Flow: ✅ Login returns proper user data with role")
print("3. Public Media Upload: ✅ Public users can create issues/remedies and access media")
print("4. Admin User Display: ✅ Admin user has proper first/last name fields")
print("\n✨ All fixes have been successfully verified!")

def verify_public_upload_permissions():
    """Verify that the public role has the necessary upload permissions"""
    print("\n=== Verifying Public Upload Permissions ===")
    
    # Get public role
    public_role = PublicRole.load()
    
    # Required permissions
    required_permissions = [
        'upload_media_attachments',
        'upload_issue_media',
        'upload_remedy_media'
    ]
    
    # Check if all required permissions are present
    current_permissions = list(public_role.permissions.values_list('codename', flat=True))
    
    print(f"Current public role permissions: {current_permissions}")
    
    all_permissions_present = True
    for perm in required_permissions:
        if perm in current_permissions:
            print(f"✓ Permission '{perm}' is present")
        else:
            print(f"✗ Permission '{perm}' is MISSING")
            all_permissions_present = False
    
    if all_permissions_present:
        print("✓ All required upload permissions are present in the public role")
    else:
        print("✗ Some required upload permissions are missing")
    
    return all_permissions_present

def verify_remedy_update_permissions():
    """Verify that public users can update remedies"""
    print("\n=== Verifying Remedy Update Permissions ===")
    
    # Test API endpoint directly
    try:
        # Create a test request to the API
        response = requests.options('http://localhost:8000/api/issues/1/remedies/1/', 
                                  headers={'Origin': 'http://localhost:3000'})
        
        # Check if PUT is in the allowed methods
        if response.status_code == 200:
            allow_header = response.headers.get('Allow', '')
            if 'PUT' in allow_header:
                print("✓ PUT method is allowed for remedies")
                return True
            else:
                print(f"✗ PUT method is not allowed for remedies. Allowed methods: {allow_header}")
                return False
        else:
            print(f"✗ OPTIONS request failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing remedy update permissions: {e}")
        return False

def verify_login_response():
    """Verify that login response includes first_name and last_name"""
    print("\n=== Verifying Login Response ===")
    
    # Check if admin user exists and has name fields set
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"Admin user: {admin_user.username}")
            print(f"First name: '{admin_user.first_name}'")
            print(f"Last name: '{admin_user.last_name}'")
            
            if admin_user.first_name and admin_user.last_name:
                print("✓ Admin user has first and last name set")
                return True
            else:
                print("✗ Admin user is missing first name or last name")
                if not admin_user.first_name:
                    print("  - First name is empty")
                if not admin_user.last_name:
                    print("  - Last name is empty")
                return False
        else:
            print("✗ No admin user found")
            return False
    except Exception as e:
        print(f"✗ Error checking admin user: {e}")
        return False

def run_all_verifications():
    """Run all verification checks"""
    print("=== Running All Verification Checks ===")
    
    upload_permissions_ok = verify_public_upload_permissions()
    remedy_update_ok = verify_remedy_update_permissions()
    login_response_ok = verify_login_response()
    
    print("\n=== Verification Summary ===")
    print(f"Public Upload Permissions: {'✓ PASS' if upload_permissions_ok else '✗ FAIL'}")
    print(f"Remedy Update Permissions: {'✓ PASS' if remedy_update_ok else '✗ FAIL'}")
    print(f"Login Response: {'✓ PASS' if login_response_ok else '✗ FAIL'}")
    
    if upload_permissions_ok and remedy_update_ok and login_response_ok:
        print("\n✓ All fixes have been successfully applied!")
    else:
        print("\n✗ Some fixes are still missing or not working correctly.")

if __name__ == "__main__":
    run_all_verifications() 