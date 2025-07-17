#!/usr/bin/env python3
"""
Test script to verify session authentication fix
"""
import requests
import json

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔍 Testing Authentication Flow...")
    
    # Create session to maintain cookies
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000/api'
    
    try:
        # Step 1: Test login
        print("\n1️⃣ Testing login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'  # Updated with correct password
        }
        
        login_response = session.post(f'{base_url}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            print(f"✅ Login successful: {login_response.status_code}")
            user_data = login_response.json()
            print(f"   User: {user_data['user']['username']}")
            print(f"   Is superuser: {user_data['user']['is_superuser']}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        # Step 2: Test current user endpoint
        print("\n2️⃣ Testing current user endpoint...")
        user_response = session.get(f'{base_url}/auth/user/')
        
        if user_response.status_code == 200:
            print(f"✅ Current user check successful: {user_response.status_code}")
            current_user = user_response.json()
            print(f"   Username: {current_user['username']}")
        else:
            print(f"❌ Current user check failed: {user_response.status_code}")
            print(f"   Response: {user_response.text}")
            return False
        
        # Step 3: Test dashboard metrics (the failing endpoint)
        print("\n3️⃣ Testing dashboard metrics endpoint...")
        dashboard_response = session.get(f'{base_url}/dashboard/metrics/?days=30')
        
        if dashboard_response.status_code == 200:
            print(f"✅ Dashboard metrics successful: {dashboard_response.status_code}")
            metrics = dashboard_response.json()
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Open issues: {metrics.get('open_issues', 'N/A')}")
            print("🎉 Session authentication is working correctly!")
            return True
        else:
            print(f"❌ Dashboard metrics failed: {dashboard_response.status_code}")
            print(f"   Response: {dashboard_response.text}")
            
            if dashboard_response.status_code == 401:
                print("   This indicates session cookies are still not working properly")
            elif dashboard_response.status_code == 403:
                print("   User doesn't have dashboard permissions - need to check user roles")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django backend on port 8000")
        print("   Make sure the Django server is running: python manage.py runserver 127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_cookies():
    """Check cookie configuration"""
    print("\n🍪 Checking cookie configuration...")
    
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000/api'
    
    try:
        # Make a login request and check cookies
        login_data = {'username': 'admin', 'password': 'admin123'}
        response = session.post(f'{base_url}/auth/login/', json=login_data)
        
        if response.status_code == 200:
            print("   Cookies received after login:")
            for cookie in session.cookies:
                print(f"     {cookie.name}: {cookie.value[:20]}...")
                print(f"       Domain: {cookie.domain}")
                print(f"       Path: {cookie.path}")
                print(f"       Secure: {cookie.secure}")
        else:
            print(f"   Login failed, cannot check cookies: {response.status_code}")
            
    except Exception as e:
        print(f"   Error checking cookies: {e}")

if __name__ == '__main__':
    print("🧪 Session Authentication Test")
    print("=" * 50)
    
    # Check cookies first
    check_cookies()
    
    # Test authentication flow
    success = test_auth_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Authentication is working correctly.")
        print("   You should now be able to access the dashboard without issues.")
    else:
        print("❌ Tests failed. Please restart the Django server and try again.")
        print("   Steps to restart:")
        print("   1. Stop the Django server (Ctrl+C)")
        print("   2. cd project/django_backend")
        print("   3. python manage.py runserver 127.0.0.1:8000")
        print("   4. Run this test again") 