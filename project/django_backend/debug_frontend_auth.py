#!/usr/bin/env python3
"""
Debug frontend authentication issues
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

BASE_URL = "http://127.0.0.1:8000/api"

def test_frontend_auth_flow():
    """Test the complete frontend authentication flow"""
    print("🔍 Testing Frontend Authentication Flow")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Step 1: Login
        print("1️⃣ Testing login...")
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f'{BASE_URL}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            print("✅ Login successful")
            print(f"   User: {user_data['user']['username']}")
            print(f"   Role: {user_data['user']['role']['role_name']}")
            
            # Check cookies
            print(f"   Session cookies: {list(session.cookies.keys())}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Step 2: Test current user endpoint
        print("\n2️⃣ Testing current user endpoint...")
        user_response = session.get(f'{BASE_URL}/auth/user/')
        
        if user_response.status_code == 200:
            current_user = user_response.json()
            print("✅ Current user endpoint working")
            print(f"   Username: {current_user['username']}")
            print(f"   Role: {current_user['role']['role_name']}")
        else:
            print(f"❌ Current user failed: {user_response.status_code}")
            print(f"   Error: {user_response.text}")
            return False
        
        # Step 3: Test dashboard access
        print("\n3️⃣ Testing dashboard access...")
        dashboard_response = session.get(f'{BASE_URL}/dashboard/metrics/')
        
        if dashboard_response.status_code == 200:
            metrics = dashboard_response.json()
            print("✅ Dashboard access working")
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Cost data: {'total_cost' in metrics}")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            print(f"   Error: {dashboard_response.text}")
        
        # Step 4: Test issue creation
        print("\n4️⃣ Testing issue creation...")
        issue_data = {
            'category': 'mechanical',
            'priority': 'medium',
            'machine_id_ref': 'FRONTEND_AUTH_TEST',
            'description': 'Test issue for frontend auth debugging',
            'reported_by': 'Admin Frontend Test'
        }
        
        create_response = session.post(f'{BASE_URL}/issues/', json=issue_data)
        
        if create_response.status_code == 201:
            issue = create_response.json()
            print("✅ Issue creation working")
            issue_id = issue['id']
            
            # Step 5: Test remedy creation
            print("\n5️⃣ Testing remedy creation...")
            remedy_data = {
                'description': 'Test remedy for frontend auth',
                'technician_name': 'Frontend Test Tech',
                'is_external': True,
                'phone_number': '555-FRONTEND',
                'labor_cost': 100.0,
                'parts_cost': 50.0,
                'is_machine_runnable': True
            }
            
            remedy_response = session.post(f'{BASE_URL}/issues/{issue_id}/remedies/', json=remedy_data)
            
            if remedy_response.status_code == 201:
                remedy = remedy_response.json()
                print("✅ Remedy creation working")
                
                # Check if cost data is visible
                cost_display = remedy.get('cost_display')
                if cost_display:
                    print(f"✅ Cost data visible: ${cost_display.get('total_cost', 'N/A')}")
                else:
                    print("❌ Cost data not visible")
                
            else:
                print(f"❌ Remedy creation failed: {remedy_response.status_code}")
                print(f"   Error: {remedy_response.text}")
            
            # Step 6: Test issue update
            print("\n6️⃣ Testing issue update...")
            update_data = {'status': 'in_progress'}
            update_response = session.patch(f'{BASE_URL}/issues/{issue_id}/', json=update_data)
            
            if update_response.status_code == 200:
                print("✅ Issue update working")
            else:
                print(f"❌ Issue update failed: {update_response.status_code}")
                print(f"   Error: {update_response.text}")
                
        else:
            print(f"❌ Issue creation failed: {create_response.status_code}")
            print(f"   Error: {create_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers and session handling"""
    print("\n🌐 Testing CORS and Session Configuration")
    print("=" * 50)
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,X-CSRFToken'
        }
        
        options_response = requests.options(f'{BASE_URL}/auth/login/', headers=headers)
        print(f"CORS preflight status: {options_response.status_code}")
        print(f"CORS headers: {dict(options_response.headers)}")
        
        # Test actual login with CORS headers
        session = requests.Session()
        session.headers.update({'Origin': 'http://localhost:3000'})
        
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f'{BASE_URL}/auth/login/', json=login_data)
        
        print(f"\nLogin with CORS headers: {login_response.status_code}")
        print(f"Response headers: {dict(login_response.headers)}")
        print(f"Set-Cookie headers: {login_response.headers.get('Set-Cookie', 'None')}")
        
    except Exception as e:
        print(f"❌ CORS test failed: {str(e)}")

def main():
    print("🧪 FRONTEND AUTHENTICATION DEBUG")
    print("=" * 60)
    
    if test_frontend_auth_flow():
        print("\n✅ Backend authentication flow is working correctly")
    else:
        print("\n❌ Backend authentication flow has issues")
    
    test_cors_headers()
    
    print("\n" + "=" * 60)
    print("If backend tests pass but frontend fails, check:")
    print("1. Frontend is making requests to correct URL")
    print("2. Frontend is including credentials in requests")
    print("3. CSRF tokens are being handled properly")
    print("4. Session cookies are being stored and sent")
    print("=" * 60)

if __name__ == "__main__":
    main() 