#!/usr/bin/env python3

import requests
import json

def test_frontend_auth():
    """Test frontend authentication flow to debug dashboard issue"""
    
    print("🔍 DEBUGGING FRONTEND AUTHENTICATION ISSUE")
    print("=" * 60)
    
    # Create session to maintain cookies
    session = requests.Session()
    base_url = "http://127.0.0.1:8000/api"
    
    # Step 1: Get CSRF token
    print("1️⃣ Getting CSRF token...")
    try:
        csrf_response = session.get(f"{base_url}/auth/csrf/")
        csrf_token = csrf_response.cookies.get('csrftoken')
        print(f"✅ CSRF token: {csrf_token[:10]}...")
    except Exception as e:
        print(f"❌ Failed to get CSRF token: {e}")
        return
    
    # Step 2: Login
    print("\n2️⃣ Testing login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': 'http://127.0.0.1:8000'
    }
    
    try:
        login_response = session.post(
            f"{base_url}/auth/login/", 
            json=login_data,
            headers=headers
        )
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            print(f"✅ Login successful")
            print(f"   Username: {user_data.get('user', {}).get('username')}")
            print(f"   Role: {user_data.get('user', {}).get('role', {}).get('role_name', 'No role')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return
    
    # Step 3: Test getCurrentUser (what AuthContext calls)
    print("\n3️⃣ Testing getCurrentUser...")
    try:
        user_response = session.get(
            f"{base_url}/auth/user/",
            headers=headers
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ getCurrentUser successful")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Role: {user_data.get('role', {}).get('role_name', 'No role')}")
        else:
            print(f"❌ getCurrentUser failed: {user_response.status_code}")
            print(f"   Response: {user_response.text}")
            
    except Exception as e:
        print(f"❌ getCurrentUser request failed: {e}")
    
    # Step 4: Test dashboard endpoint (the problematic one)
    print("\n4️⃣ Testing dashboard metrics...")
    try:
        # Update CSRF token from session cookies
        current_csrf = session.cookies.get('csrftoken')
        if current_csrf:
            headers['X-CSRFToken'] = current_csrf
        
        dashboard_response = session.get(
            f"{base_url}/dashboard/metrics/?days=30",
            headers=headers
        )
        
        if dashboard_response.status_code == 200:
            metrics = dashboard_response.json()
            print(f"✅ Dashboard metrics successful")
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Open issues: {metrics.get('open_issues', 'N/A')}")
        else:
            print(f"❌ Dashboard metrics failed: {dashboard_response.status_code}")
            print(f"   Response: {dashboard_response.text}")
            
    except Exception as e:
        print(f"❌ Dashboard request failed: {e}")
    
    # Step 5: Show session cookies
    print("\n5️⃣ Current session cookies:")
    for cookie in session.cookies:
        print(f"   {cookie.name}: {cookie.value[:20]}...")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("If all tests pass, the backend is working fine.")
    print("The issue is likely in the frontend session management.")

if __name__ == "__main__":
    test_frontend_auth() 