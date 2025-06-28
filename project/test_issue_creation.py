#!/usr/bin/env python3

import requests
import json

def test_issue_creation():
    """Test issue creation endpoint"""
    
    # Test data
    issue_data = {
        "machine_id_ref": "A1",  # You may need to adjust this based on your actual machine IDs
        "category": "mechanical",
        "description": "Test issue for debugging",
        "is_runnable": True,
        "priority": "medium",
        "reported_by": "Test User",
        "alarm_code": None,
    }
    
    print("Testing issue creation...")
    print(f"Data to send: {json.dumps(issue_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/issues/",
            json=issue_data,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Issue created successfully!")
            print(f"Response data: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Issue creation failed!")
            print(f"Response content: {response.text}")
            
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Make sure it's running on port 8000.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def test_departments():
    """Test departments endpoint"""
    print("\nTesting departments endpoint...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/departments/", timeout=10)
        print(f"Departments response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', []))} departments")
            if data.get('results'):
                print("Sample department:", data['results'][0])
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing departments: {str(e)}")

def test_machines():
    """Test machines endpoint"""
    print("\nTesting machines endpoint...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/machines/", timeout=10)
        print(f"Machines response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', []))} machines")
            if data.get('results'):
                print("Sample machine:", data['results'][0])
                print("Available machine IDs:", [m['machine_id'] for m in data['results'][:5]])
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing machines: {str(e)}")

if __name__ == "__main__":
    test_departments()
    test_machines()
    test_issue_creation() 