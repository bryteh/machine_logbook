#!/usr/bin/env python3
"""
Test all admin authentication fixes
"""
import os
import sys
import django
import requests
import json
import tempfile
from PIL import Image

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy

BASE_URL = "http://127.0.0.1:8000/api"

def test_admin_login():
    """Test admin login"""
    print("🔐 Testing Admin Login")
    print("=" * 40)
    
    try:
        session = requests.Session()
        
        # Get CSRF token first
        csrf_response = session.get(f'{BASE_URL}/auth/login/')
        if 'csrftoken' in session.cookies:
            session.headers.update({'X-CSRFToken': session.cookies['csrftoken']})
        
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f'{BASE_URL}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            print("✅ Admin login successful")
            print(f"   Role: {user_data['user']['role']['role_name']}")
            print(f"   Permissions: {len(user_data['user']['role']['permissions'])} permissions")
            return session
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return None
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
        return None

def test_dashboard_access(session):
    """Test dashboard metrics access"""
    print("\n📊 Testing Dashboard Access")
    print("=" * 40)
    
    try:
        dashboard_response = session.get(f'{BASE_URL}/dashboard/metrics/')
        
        if dashboard_response.status_code == 200:
            metrics = dashboard_response.json()
            print("✅ Dashboard access successful")
            print(f"   Total issues: {metrics.get('total_issues', 'N/A')}")
            print(f"   Cost data included: {'total_cost' in metrics}")
            return True
        else:
            print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
            print(f"   Error: {dashboard_response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False

def test_issue_creation(session):
    """Test issue creation as admin"""
    print("\n📝 Testing Issue Creation")
    print("=" * 40)
    
    try:
        issue_data = {
            'category': 'mechanical',
            'priority': 'medium',
            'machine_id_ref': 'ADMIN_FIX_TEST_001',
            'description': 'Test issue for admin fix verification',
            'reported_by': 'Admin Test'
        }
        
        create_response = session.post(f'{BASE_URL}/issues/', json=issue_data)
        
        if create_response.status_code == 201:
            issue = create_response.json()
            print("✅ Issue creation successful")
            print(f"   Issue ID: {issue['id']}")
            return issue['id']
        else:
            print(f"❌ Issue creation failed: {create_response.status_code}")
            print(f"   Error: {create_response.text}")
            return None
    except Exception as e:
        print(f"❌ Issue creation test failed: {str(e)}")
        return None

def test_issue_update(session, issue_id):
    """Test issue update as admin"""
    print("\n✏️ Testing Issue Update")
    print("=" * 40)
    
    try:
        update_data = {
            'description': 'Updated test issue for admin fix verification - UPDATED',
            'status': 'in_progress'
        }
        
        update_response = session.patch(f'{BASE_URL}/issues/{issue_id}/', json=update_data)
        
        if update_response.status_code == 200:
            issue = update_response.json()
            print("✅ Issue update successful")
            print(f"   Status: {issue.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Issue update failed: {update_response.status_code}")
            print(f"   Error: {update_response.text}")
            return False
    except Exception as e:
        print(f"❌ Issue update test failed: {str(e)}")
        return False

def test_remedy_creation(session, issue_id):
    """Test remedy creation as admin with cost visibility"""
    print("\n🔧 Testing Remedy Creation & Cost Visibility")
    print("=" * 40)
    
    try:
        remedy_data = {
            'description': 'Test remedy for admin cost visibility',
            'technician_name': 'Admin Tech',
            'is_external': True,
            'phone_number': '555-ADMIN',
            'labor_cost': 150.75,
            'parts_cost': 89.25,
            'is_machine_runnable': True
        }
        
        create_response = session.post(f'{BASE_URL}/issues/{issue_id}/remedies/', json=remedy_data)
        
        if create_response.status_code == 201:
            remedy = create_response.json()
            print("✅ Remedy creation successful")
            print(f"   Remedy ID: {remedy['id']}")
            
            # Check cost visibility
            cost_display = remedy.get('cost_display')
            phone_display = remedy.get('phone_display')
            
            if cost_display and cost_display.get('labor_cost') is not None:
                print(f"✅ Cost data visible: Labor ${cost_display['labor_cost']}, Parts ${cost_display['parts_cost']}")
            else:
                print("❌ Cost data not visible for admin")
            
            if phone_display:
                print(f"✅ Phone number visible: {phone_display}")
            else:
                print("❌ Phone number not visible for admin")
            
            return remedy['id']
        else:
            print(f"❌ Remedy creation failed: {create_response.status_code}")
            print(f"   Error: {create_response.text}")
            return None
    except Exception as e:
        print(f"❌ Remedy creation test failed: {str(e)}")
        return None

def test_issue_detail_cost_visibility(session, issue_id):
    """Test issue detail cost visibility for admin"""
    print("\n💰 Testing Issue Detail Cost Visibility")
    print("=" * 40)
    
    try:
        detail_response = session.get(f'{BASE_URL}/issues/{issue_id}/')
        
        if detail_response.status_code == 200:
            issue = detail_response.json()
            print("✅ Issue detail access successful")
            
            remedies = issue.get('remedies', [])
            if remedies:
                remedy = remedies[0]
                cost_display = remedy.get('cost_display')
                phone_display = remedy.get('phone_display')
                
                if cost_display:
                    print(f"✅ Cost visible in issue detail: Total ${cost_display.get('total_cost', 'N/A')}")
                else:
                    print("❌ Cost not visible in issue detail")
                
                if phone_display:
                    print(f"✅ Phone visible in issue detail: {phone_display}")
                else:
                    print("❌ Phone not visible in issue detail")
                
                return cost_display is not None
            else:
                print("❌ No remedies found in issue detail")
                return False
        else:
            print(f"❌ Issue detail access failed: {detail_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Issue detail test failed: {str(e)}")
        return False

def main():
    print("🧪 ADMIN AUTHENTICATION FIXES TEST")
    print("=" * 60)
    
    # Test authentication
    session = test_admin_login()
    if not session:
        print("\n⚠️ Admin login failed. Cannot continue tests.")
        return
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Dashboard access
    if test_dashboard_access(session):
        tests_passed += 1
    
    # Test 2: Issue creation
    issue_id = test_issue_creation(session)
    if issue_id:
        tests_passed += 1
        
        # Test 3: Issue update
        if test_issue_update(session, issue_id):
            tests_passed += 1
        
        # Test 4: Remedy creation with cost visibility
        remedy_id = test_remedy_creation(session, issue_id)
        if remedy_id:
            tests_passed += 1
        
        # Test 5: Issue detail cost visibility
        if test_issue_detail_cost_visibility(session, issue_id):
            tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 ADMIN FIXES TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("🎉 ALL ADMIN AUTHENTICATION ISSUES FIXED!")
        print("\n✅ Dashboard access - WORKING")
        print("✅ Issue creation - WORKING")
        print("✅ Issue editing - WORKING")
        print("✅ Remedy creation - WORKING")
        print("✅ Cost visibility - WORKING")
    else:
        print(f"⚠️ {total_tests - tests_passed} issues still need attention")

if __name__ == "__main__":
    main() 