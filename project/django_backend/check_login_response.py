#!/usr/bin/env python
import requests
import json
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import PublicRole

print("🔍 Checking Login Response & Public Permissions")
print("=" * 50)

# Test 1: Check login response data
print("1️⃣ Login Response Analysis")
try:
    login_data = {'username': 'admin', 'password': 'admin123'}
    response = requests.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
    
    if response.status_code == 200:
        user_data = response.json()['user']
        print("✅ Login successful")
        print(f"Username: {user_data['username']}")
        print(f"Is Staff: {user_data['is_staff']}")
        print(f"Is Superuser: {user_data['is_superuser']}")
        
        if user_data['role']:
            role = user_data['role']
            print(f"Role: {role['role']}")
            print(f"Role Name: {role['role_name']}")
            print(f"Permissions: {role['permissions']}")
            print(f"Has view_dashboard: {'view_dashboard' in role['permissions']}")
        else:
            print("❌ No role data in login response!")
    else:
        print(f"❌ Login failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check current public permissions
print("\n2️⃣ Public Role Permissions")
try:
    public_role = PublicRole.load()
    print("✅ Public role loaded")
    print(f"Current permissions: {public_role.permissions}")
    print(f"Can create issues: {public_role.has_permission('crud_issues')}")
    print(f"Can create remedies: {public_role.has_permission('crud_remedies')}")
    print(f"Can view costs: {public_role.has_permission('view_costs')}")
    print(f"Can view external contacts: {public_role.has_permission('view_external_contacts')}")
    
except Exception as e:
    print(f"❌ Error loading public role: {e}")

print("\n" + "=" * 50)
print("Analysis complete") 