#!/usr/bin/env python3
"""
Debug dashboard metrics endpoint issue
"""
import requests
import json

def test_dashboard_issue():
    print("🔍 DEBUGGING DASHBOARD METRICS ISSUE")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Step 1: Login first
        print("1️⃣ Testing admin login...")
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post('http://127.0.0.1:8000/api/auth/login/', 
                                    json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            user_data = login_response.json()
            print(f"   Username: {user_data['user']['username']}")
            print(f"   Role: {user_data['user']['role']['role_name']}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Step 2: Test dashboard metrics endpoint
        print("\n2️⃣ Testing dashboard metrics endpoint...")
        
        # Get CSRF token from cookies
        csrf_token = None
        for cookie in session.cookies:
            if cookie.name == 'csrftoken':
                csrf_token = cookie.value
                break
        
        headers = {
            'Content-Type': 'application/json',
        }
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
            
        print(f"   Using CSRF token: {csrf_token[:10] if csrf_token else 'None'}...")
        print(f"   Session cookies: {list(session.cookies.keys())}")
        
        dashboard_response = session.get('http://127.0.0.1:8000/api/dashboard/metrics/', 
                                       headers=headers, timeout=10)
        
        print(f"   Dashboard response status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            metrics = dashboard_response.json()
            print("✅ Dashboard metrics working!")
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Open issues: {metrics.get('open_issues', 'N/A')}")
            print(f"   Total cost: ${metrics.get('total_cost', 'N/A')}")
        else:
            print(f"❌ Dashboard metrics failed!")
            print(f"   Error: {dashboard_response.text}")
            print(f"   Response headers: {dict(dashboard_response.headers)}")
            
        # Step 3: Test with frontend-like request
        print("\n3️⃣ Testing with frontend-style headers...")
        frontend_headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://127.0.0.1:5183',
            'Referer': 'http://127.0.0.1:5183/',
        }
        if csrf_token:
            frontend_headers['X-CSRFToken'] = csrf_token
            
        frontend_response = session.get('http://127.0.0.1:8000/api/dashboard/metrics/', 
                                       headers=frontend_headers, timeout=10)
        
        print(f"   Frontend-style request status: {frontend_response.status_code}")
        if frontend_response.status_code != 200:
            print(f"   Error: {frontend_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_dashboard_issue() 