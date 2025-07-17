#!/usr/bin/env python
"""
Test the /remedies/ endpoint specifically
"""
import requests
import json

def test_remedies_endpoint():
    """Test the /remedies/ endpoint"""
    print("🔍 Testing /remedies/ Endpoint")
    print("=" * 50)
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # First create an issue
    issue_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'machine_id_ref': 'TEST003',
        'location': 'Test Location',
        'description': 'Test issue for remedies endpoint',
        'occurrence_datetime': '2024-01-01T10:00:00Z',
        'reported_by': 'Test User'
    }
    
    try:
        # Create issue
        response = requests.post(f'{base_url}/issues/', json=issue_data, timeout=5)
        print(f"📊 Issue Creation Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"❌ Issue creation failed: {response.text}")
            return False
            
        issue_id = response.json().get('id')
        print(f"✅ Issue created: {issue_id}")
        
        # Test /remedies/ endpoint
        remedy_data = {
            'description': 'Test remedy via /remedies/ endpoint',
            'technician_name': 'Test Technician',
            'is_external': False,
            'is_machine_runnable': True
        }
        
        print(f"\n🧪 Testing POST /issues/{issue_id}/remedies/")
        response = requests.post(f'{base_url}/issues/{issue_id}/remedies/', json=remedy_data, timeout=5)
        print(f"📊 Remedy Creation Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Remedy created successfully via /remedies/")
            remedy_response = response.json()
            print(f"🆔 Remedy ID: {remedy_response.get('id')}")
            return True
        else:
            print(f"❌ Remedy creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_remedies_endpoint()
    if success:
        print("\n🎉 /remedies/ endpoint is working correctly!")
    else:
        print("\n❌ /remedies/ endpoint has issues") 