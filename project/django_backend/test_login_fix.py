#!/usr/bin/env python
"""
Test login functionality with correct credentials
"""
import requests
import json

def test_login():
    """Test the login functionality"""
    
    # Test data
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    user_url = "http://127.0.0.1:8000/api/auth/user/"
    
    # Test with admin credentials
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("Testing login functionality...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test login
        print(f"Attempting login at {login_url}")
        response = session.post(login_url, json=login_data)
        
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            login_response_data = response.json()
            print("✓ Login successful!")
            print(f"Response data: {json.dumps(login_response_data, indent=2)}")
            
            # Check if user data is in the response
            if 'user' in login_response_data:
                user_data = login_response_data['user']
                print(f"User data received: {user_data}")
                
                # Check if first_name and last_name are present
                if user_data.get('first_name') and user_data.get('last_name'):
                    print("✓ User has first and last name")
                else:
                    print("✗ User missing first or last name")
                    print(f"  First name: '{user_data.get('first_name', 'MISSING')}'")
                    print(f"  Last name: '{user_data.get('last_name', 'MISSING')}'")
                
                # Test if we can access the user endpoint
                print(f"\nTesting authenticated user endpoint at {user_url}")
                user_response = session.get(user_url)
                print(f"User endpoint response status: {user_response.status_code}")
                
                if user_response.status_code == 200:
                    print("✓ Can access user endpoint after login")
                    user_endpoint_data = user_response.json()
                    print(f"User endpoint data: {json.dumps(user_endpoint_data, indent=2)}")
                else:
                    print(f"✗ Cannot access user endpoint: {user_response.text}")
            else:
                print("✗ No user data in login response")
        else:
            print(f"✗ Login failed: {response.text}")
    
    except Exception as e:
        print(f"Error during login test: {e}")
        import traceback
        traceback.print_exc()

def test_public_issue_creation():
    """Test public issue creation"""
    print("\n🔍 Testing Public Issue Creation")
    print("=" * 40)
    
    url = 'http://localhost:8000/api/issues/'
    
    issue_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'machine_id_ref': 'TEST002',
        'description': 'Test issue from public user',
        'reported_by': 'Public User',
        'alarm_code': 'TEST-002'
    }
    
    try:
        response = requests.post(url, json=issue_data)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 201:
            response_json = response.json()
            print(f"✅ SUCCESS: Public issue creation works")
            print(f"📝 Issue: {json.dumps(response_json, indent=2)}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Login and Public Access")
    print("=" * 60)
    
    test_login()
    test2 = test_public_issue_creation()
    
    print("\n" + "=" * 60)
    print("📋 Results:")
    print(f"  Login Test: {'✅ PASS' if test_login() else '❌ FAIL'}")
    print(f"  Public Issue Creation: {'✅ PASS' if test2 else '❌ FAIL'}") 