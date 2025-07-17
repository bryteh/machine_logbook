#!/usr/bin/env python
import requests
import json

# Test login with admin credentials
data = {'username': 'admin', 'password': 'admin123'}
try:
    r = requests.post('http://127.0.0.1:8000/api/auth/login/', json=data, timeout=5)
    print(f'Login Status: {r.status_code}')
    print(f'Response: {r.text[:300]}')
    
    if r.status_code == 200:
        print("✅ Login working correctly")
    else:
        print("❌ Login failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test remedy creation without auth
print("\n" + "="*50)
print("Testing public remedy creation...")

# First create a test issue
issue_data = {
    'category': 'mechanical',
    'priority': 'medium', 
    'machine_id_ref': 'TEST001',
    'description': 'Test issue',
    'reported_by': 'Public User'
}

try:
    # Create issue
    r = requests.post('http://127.0.0.1:8000/api/issues/', json=issue_data, timeout=5)
    print(f'Issue creation status: {r.status_code}')
    
    if r.status_code == 201:
        issue_id = r.json()['id']
        print(f'✅ Issue created: {issue_id}')
        
        # Create remedy
        remedy_data = {
            'description': 'Test remedy',
            'technician_name': 'Public Tech',
            'is_external': True,
            'phone_number': '123-456-7890',
            'is_machine_runnable': True
        }
        
        r = requests.post(f'http://127.0.0.1:8000/api/issues/{issue_id}/remedies/', json=remedy_data, timeout=5)
        print(f'Remedy creation status: {r.status_code}')
        
        if r.status_code == 201:
            print("✅ Public remedy creation working correctly")
        else:
            print(f"❌ Remedy creation failed: {r.text}")
    else:
        print(f"❌ Issue creation failed: {r.text}")
        
except Exception as e:
    print(f"❌ Error: {e}") 