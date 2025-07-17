#!/usr/bin/env python
"""
Test public access functionality
"""
import requests
import json

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
        'machine_id_ref': 'TEST002',
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
                'description': 'Test remedy for public access verification',
                'technician_name': 'Public Technician',
                'phone_number': '123-456-7890',
                'is_external': True,
                'is_machine_runnable': False
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
                    return True
                else:
                    print(f"❌ Add remedy failed: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Add remedy error: {e}")
                return False
                
        else:
            print(f"❌ Issue creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Issue creation error: {e}")
        return False

if __name__ == "__main__":
    success = test_public_access()
    if success:
        print("\n🎉 ALL TESTS PASSED - Public access is working!")
    else:
        print("\n❌ TESTS FAILED - Issues with public access") 