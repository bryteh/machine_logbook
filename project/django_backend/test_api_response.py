#!/usr/bin/env python
"""
Test API responses with correct IP address
"""
import requests
import json
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue

def test_api_endpoints():
    """Test API endpoints with 127.0.0.1"""
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # Test 1: Login
    print("\n1️⃣ Testing Login")
    login_data = {'username': 'admin', 'password': 'admin123'}
    try:
        response = requests.post(f'{base_url}/auth/login/', json=login_data, timeout=5)
        print(f"📊 Login Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login successful")
            user_data = response.json()
            print(f"👤 User: {user_data.get('user', {}).get('username')}")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 2: Public Issue Creation
    print("\n2️⃣ Testing Public Issue Creation")
    issue_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'machine_id_ref': 'TEST001',
        'location': 'Test Location',
        'description': 'Test issue for API verification',
        'occurrence_datetime': '2024-01-01T10:00:00Z'
    }
    try:
        response = requests.post(f'{base_url}/issues/', json=issue_data, timeout=5)
        print(f"📊 Issue Creation Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Issue creation successful")
            issue_id = response.json().get('id')
            print(f"🆔 Issue ID: {issue_id}")
            
            # Test 3: Public Remedy Creation
            print("\n3️⃣ Testing Public Remedy Creation")
            remedy_data = {
                'action_taken': 'Test remedy for API verification',
                'external_technician_name': 'Test Technician',
                'external_contact_number': '123-456-7890',
                'remedy_format': 'text',
                'cost': 0
            }
            
            # Test both endpoints
            endpoints = [
                f'/issues/{issue_id}/remedies/',
                f'/issues/{issue_id}/add_remedy/'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(f'{base_url}{endpoint}', json=remedy_data, timeout=5)
                    print(f"📊 Remedy ({endpoint}) Status: {response.status_code}")
                    if response.status_code == 201:
                        print(f"✅ Remedy creation successful via {endpoint}")
                    else:
                        print(f"❌ Remedy creation failed via {endpoint}: {response.text}")
                except Exception as e:
                    print(f"❌ Remedy error via {endpoint}: {e}")
        else:
            print(f"❌ Issue creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Issue creation error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API Test Complete")

if __name__ == "__main__":
    test_api_endpoints()