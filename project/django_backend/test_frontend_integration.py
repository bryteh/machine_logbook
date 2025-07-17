#!/usr/bin/env python3
"""
Test frontend integration with authentication fixes
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

def test_admin_authentication_workflow():
    """Test the complete admin authentication workflow"""
    print("🔐 TESTING ADMIN AUTHENTICATION WORKFLOW")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({'Origin': 'http://localhost:3000'})
    
    try:
        # Step 1: Login as admin
        print("1️⃣ Testing admin login...")
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f'{BASE_URL}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            print("✅ Login successful")
            print(f"   User: {user_data['user']['username']}")
            print(f"   Role: {user_data['user']['role']['role_name']}")
            print(f"   Permissions: {len(user_data['user']['role']['permissions'])} permissions")
            
            # Check session cookies
            print(f"   Session cookies: {list(session.cookies.keys())}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
        
        # Step 2: Test current user endpoint (like frontend does)
        print("\n2️⃣ Testing current user endpoint...")
        current_user_response = session.get(f'{BASE_URL}/auth/user/')
        
        if current_user_response.status_code == 200:
            current_user = current_user_response.json()
            print("✅ Current user endpoint working")
            print(f"   Username: {current_user['username']}")
            print(f"   Role: {current_user['role']['role_name']}")
            print(f"   Is superuser: {current_user['is_superuser']}")
            print(f"   Can view costs: {current_user['role']['can_view_costs']}")
        else:
            print(f"❌ Current user failed: {current_user_response.status_code}")
            print(f"   Error: {current_user_response.text}")
            return False
        
        # Step 3: Test dashboard access
        print("\n3️⃣ Testing dashboard access...")
        dashboard_response = session.get(f'{BASE_URL}/dashboard/metrics/')
        
        if dashboard_response.status_code == 200:
            metrics = dashboard_response.json()
            print("✅ Dashboard access successful")
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Cost data available: {'total_cost' in metrics}")
            if 'total_cost' in metrics:
                print(f"   Total cost: ${metrics['total_cost']:.2f}")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            print(f"   Error: {dashboard_response.text}")
            return False
        
        # Step 4: Test authenticated issue creation
        print("\n4️⃣ Testing admin issue creation...")
        
        # First get CSRF token
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("❌ No CSRF token available")
            return False
        
        print(f"   Using CSRF token: {csrf_token[:10]}...")
        
        issue_data = {
            'category': 'mechanical',
            'priority': 'high',
            'machine_id_ref': 'ADMIN_TEST_001',
            'description': 'Admin authentication test issue',
            'reported_by': 'Admin User',
            'downtime_hours': 2.5
        }
        
        # Add CSRF token to headers
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        create_response = session.post(f'{BASE_URL}/issues/', 
                                     json=issue_data, 
                                     headers=headers)
        
        if create_response.status_code == 201:
            issue = create_response.json()
            print("✅ Admin issue creation working")
            issue_id = issue['id']
            
            # Step 5: Test authenticated remedy creation
            print("\n5️⃣ Testing admin remedy creation...")
            remedy_data = {
                'description': 'Admin remedy test',
                'technician_name': 'Admin Test Technician',
                'is_external': False,
                'labor_cost': 150.0,
                'parts_cost': 75.0,
                'is_machine_runnable': True
            }
            
            remedy_response = session.post(f'{BASE_URL}/issues/{issue_id}/remedies/',
                                         json=remedy_data,
                                         headers=headers)
            
            if remedy_response.status_code == 201:
                remedy = remedy_response.json()
                print("✅ Admin remedy creation working")
                
                # Check if cost data is visible to admin
                if 'labor_cost' in remedy and 'parts_cost' in remedy:
                    print(f"✅ Cost data visible to admin: Labor ${remedy['labor_cost']}, Parts ${remedy['parts_cost']}")
                else:
                    print("❌ Cost data not visible to admin")
                    
            else:
                print(f"❌ Admin remedy creation failed: {remedy_response.status_code}")
                print(f"   Error: {remedy_response.text}")
                return False
            
            # Step 6: Test issue update
            print("\n6️⃣ Testing admin issue update...")
            update_data = {'status': 'in_progress'}
            
            update_response = session.patch(f'{BASE_URL}/issues/{issue_id}/',
                                          json=update_data,
                                          headers=headers)
            
            if update_response.status_code == 200:
                print("✅ Admin issue update working")
            else:
                print(f"❌ Admin issue update failed: {update_response.status_code}")
                print(f"   Error: {update_response.text}")
                return False
                
        else:
            print(f"❌ Admin issue creation failed: {create_response.status_code}")
            print(f"   Error: {create_response.text}")
            
            # Debug CSRF token issue
            if create_response.status_code == 403:
                print("   🔍 Debugging CSRF issue:")
                print(f"   Session cookies: {dict(session.cookies)}")
                print(f"   Request headers: {headers}")
                
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Admin authentication workflow test failed: {str(e)}")
        return False

def test_frontend_data_structures():
    """Test that API responses match what the frontend expects"""
    print("\n📊 TESTING FRONTEND DATA STRUCTURES")
    print("=" * 60)
    
    session = requests.Session()
    
    try:
        # Login and check data structure
        print("1️⃣ Testing login response structure...")
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f'{BASE_URL}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            
            # Check login response structure (should have 'user' key)
            if 'user' in login_data:
                print("✅ Login response has correct structure (user wrapped in 'user' key)")
                user = login_data['user']
                if 'role' in user and user['role']:
                    print("✅ Role data present in login response")
                else:
                    print("❌ Role data missing in login response")
            else:
                print("❌ Login response missing 'user' key")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Test current user endpoint
        print("\n2️⃣ Testing current user response structure...")
        current_user_response = session.get(f'{BASE_URL}/auth/user/')
        
        if current_user_response.status_code == 200:
            current_user_data = current_user_response.json()
            
            # Check current user response structure (should be direct user data)
            if 'username' in current_user_data:
                print("✅ Current user response has correct structure (direct user data)")
                if 'role' in current_user_data and current_user_data['role']:
                    print("✅ Role data present in current user response")
                else:
                    print("❌ Role data missing in current user response")
            else:
                print("❌ Current user response has wrong structure")
                return False
        else:
            print(f"❌ Current user failed: {current_user_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend data structure test failed: {str(e)}")
        return False

def main():
    print("🧪 FRONTEND INTEGRATION TEST")
    print("=" * 80)
    
    auth_success = test_admin_authentication_workflow()
    data_success = test_frontend_data_structures()
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY:")
    print(f"   Admin Authentication Workflow: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"   Frontend Data Structures: {'✅ PASS' if data_success else '❌ FAIL'}")
    
    if auth_success and data_success:
        print("\n🎉 ALL TESTS PASSED! Frontend integration should be working correctly.")
        print("\n📋 Frontend should now be able to:")
        print("   • Login admin users successfully")
        print("   • Show dashboard with cost data")
        print("   • Create and edit issues and remedies")
        print("   • Handle authentication state correctly")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 