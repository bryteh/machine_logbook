#!/usr/bin/env python
"""
Test public access functionality including issue and remedy creation
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

from issues.models import Issue, Remedy

def test_public_access():
    """Test all public access functionality"""
    print("🔍 Testing Public Access Functionality")
    print("=" * 60)
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # Test 1: Login (verify server is working)
    print("\n1️⃣ Testing Login (Server Verification)")
    login_data = {'username': 'admin', 'password': 'admin123'}
    try:
        response = requests.post(f'{base_url}/auth/login/', json=login_data, timeout=5)
        print(f"📊 Login Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is working correctly")
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
    
    # Test 2: Public Issue Creation with required fields
    print("\n2️⃣ Testing Public Issue Creation")
    issue_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'machine_id_ref': 'TEST001',
        'location': 'Test Location',
        'description': 'Test issue for public access verification',
        'occurrence_datetime': '2024-01-01T10:00:00Z',
        'reported_by': 'Public User'  # Required field
    }
    
    try:
        response = requests.post(f'{base_url}/issues/', json=issue_data, timeout=5)
        print(f"📊 Issue Creation Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Public issue creation successful")
            issue_data_response = response.json()
            issue_id = issue_data_response.get('id')
            print(f"🆔 Issue ID: {issue_id}")
            
            # Test 3: Public Remedy Creation via add_remedy endpoint
            print("\n3️⃣ Testing Public Remedy Creation")
            remedy_data = {
                'action_taken': 'Test remedy for public access verification',
                'external_technician_name': 'Public Technician',
                'external_contact_number': '123-456-7890',
                'remedy_format': 'text',
                'cost': 0
            }
            
            # Test the add_remedy endpoint (what frontend uses)
            print("\n📋 Testing /add_remedy/ endpoint (Frontend Route):")
            try:
                response = requests.post(f'{base_url}/issues/{issue_id}/add_remedy/', json=remedy_data, timeout=5)
                print(f"📊 Add Remedy Status: {response.status_code}")
                if response.status_code == 201:
                    print("✅ Public remedy creation successful via add_remedy")
                    remedy_response = response.json()
                    print(f"🆔 Remedy ID: {remedy_response.get('id')}")
                else:
                    print(f"❌ Add remedy failed: {response.text}")
            except Exception as e:
                print(f"❌ Add remedy error: {e}")
            
            # Test the remedies endpoint as alternative
            print("\n📋 Testing /remedies/ endpoint (Alternative Route):")
            try:
                response = requests.post(f'{base_url}/issues/{issue_id}/remedies/', json=remedy_data, timeout=5)
                print(f"📊 Remedies Status: {response.status_code}")
                if response.status_code == 201:
                    print("✅ Public remedy creation successful via remedies")
                else:
                    print(f"❌ Remedies failed: {response.text}")
            except Exception as e:
                print(f"❌ Remedies error: {e}")
                
        else:
            print(f"❌ Issue creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Issue creation error: {e}")
        return False
    
    # Test 4: Verify data in database
    print("\n4️⃣ Verifying Database Records")
    try:
        total_issues = Issue.objects.count()
        total_remedies = Remedy.objects.count()
        print(f"📊 Total Issues in DB: {total_issues}")
        print(f"📊 Total Remedies in DB: {total_remedies}")
        
        # Check if our test issue exists
        test_issue = Issue.objects.filter(machine_id_ref='TEST001').first()
        if test_issue:
            print(f"✅ Test issue found in database: {test_issue.id}")
            test_remedies = test_issue.remedies.count()
            print(f"📊 Remedies for test issue: {test_remedies}")
        else:
            print("❌ Test issue not found in database")
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Public Access Test Complete")
    return True

if __name__ == "__main__":
    test_public_access() 