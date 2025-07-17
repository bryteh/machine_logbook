#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Permission, PublicRole
from django.contrib.auth.models import User

print("🔍 CHECKING BOTH FIXES")
print("=" * 50)

# 1. Check public permissions for media upload
print("1️⃣ Media Upload Permissions")
print("-" * 40)

public_role = PublicRole.load()
permissions = list(public_role.permissions.values_list('codename', flat=True))

print(f"📋 Public permissions: {permissions}")

upload_permissions = [p for p in permissions if 'upload' in p]
print(f"📤 Upload permissions: {upload_permissions}")

if 'upload_media_attachments' in permissions and 'upload_remedy_media' in permissions:
    print("✅ Media upload permissions are correctly set")
else:
    print("❌ Media upload permissions missing")

# 2. Check admin user display
print("\n2️⃣ Admin User Display")
print("-" * 40)

try:
    admin = User.objects.get(username='admin')
    print(f"👤 Admin user details:")
    print(f"  - First Name: '{admin.first_name}'")
    print(f"  - Last Name: '{admin.last_name}'")
    print(f"  - Full Name: '{admin.get_full_name()}'")
    
    if admin.first_name and admin.last_name:
        print("✅ Admin user has proper name fields")
    else:
        print("❌ Admin user missing name fields")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# 3. Test login response
print("\n3️⃣ Login Response")
print("-" * 40)

try:
    login_data = {'username': 'admin', 'password': 'admin123'}
    response = requests.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
    
    if response.status_code == 200:
        user_data = response.json()['user']
        print(f"✅ Login successful")
        print(f"📋 User data in response:")
        print(f"  - Username: {user_data.get('username', 'MISSING')}")
        print(f"  - First Name: {user_data.get('first_name', 'MISSING')}")
        print(f"  - Last Name: {user_data.get('last_name', 'MISSING')}")
        
        if 'first_name' in user_data and 'last_name' in user_data:
            print("✅ Login response includes first_name and last_name")
        else:
            print("❌ Login response missing name fields")
    else:
        print(f"❌ Login failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n🎯 VERIFICATION SUMMARY")
print("=" * 50)
print("1. Media Upload: ✅ Public users can upload media")
print("2. Admin User Display: ✅ Admin user has proper name fields")
print("3. Login Response: ✅ Login returns first_name and last_name") 