#!/usr/bin/env python3
"""
Debug script to identify the exact issue with report generation
"""

import os
import sys
import django
from django.conf import settings
import traceback
import requests
import json

# Add the project path to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, Remedy
from issues.report_generator import MaintenanceReportGenerator
from django.contrib.auth.models import User
from issues.models import UserRole, Role

def check_backend_logs():
    """Check if there are any backend errors"""
    print("🔍 BACKEND DEBUGGING")
    print("=" * 50)
    
    # Test 1: Check if Django is running
    try:
        response = requests.get('http://127.0.0.1:8000/api/issues/', timeout=5)
        print(f"✅ Django backend is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Django backend is NOT running!")
        print("   Please start Django with: python manage.py runserver 127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Django: {e}")
        return False
    
    return True

def check_permissions_and_users():
    """Check user permissions and roles"""
    print("\n🔐 PERMISSIONS & USERS CHECK")
    print("=" * 40)
    
    # Check if there are any users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    if users.count() == 0:
        print("❌ No users found! You need to create a user first.")
        return False
    
    # Check users with roles
    user_roles = UserRole.objects.all()
    print(f"Users with roles: {user_roles.count()}")
    
    for user_role in user_roles:
        print(f"  - {user_role.user.username}: {user_role.role.name}")
        if user_role.role.has_permission('generate_reports'):
            print(f"    ✅ Can generate reports")
        else:
            print(f"    ❌ Cannot generate reports")
    
    return True

def check_resolved_issues():
    """Check if there are resolved issues available"""
    print("\n📋 RESOLVED ISSUES CHECK")
    print("=" * 30)
    
    # Check all issues
    all_issues = Issue.objects.all()
    resolved_issues = Issue.objects.filter(status='resolved')
    
    print(f"Total issues: {all_issues.count()}")
    print(f"Resolved issues: {resolved_issues.count()}")
    
    if resolved_issues.count() == 0:
        print("❌ No resolved issues found!")
        print("   You need to mark at least one issue as 'resolved' to generate reports.")
        
        # Show available issues
        if all_issues.count() > 0:
            print("\n   Available issues to resolve:")
            for issue in all_issues[:5]:  # Show first 5
                print(f"   - {issue.auto_title} (Status: {issue.status})")
        
        return False
    
    # Show resolved issues
    print("\n   Available resolved issues:")
    for issue in resolved_issues[:3]:  # Show first 3
        print(f"   - {issue.auto_title}")
        print(f"     ID: {issue.id}")
        print(f"     Department: {issue.department.name if issue.department else 'None'}")
        print(f"     Machine: {issue.machine.model if issue.machine else 'None'}")
        print(f"     Remedies: {issue.remedies.count()}")
    
    return True

def test_api_endpoint():
    """Test the actual API endpoint that's failing"""
    print("\n🌐 API ENDPOINT TEST")
    print("=" * 25)
    
    # Get a resolved issue
    resolved_issue = Issue.objects.filter(status='resolved').first()
    if not resolved_issue:
        print("❌ No resolved issue to test with")
        return False
    
    print(f"Testing with issue: {resolved_issue.auto_title}")
    print(f"Issue ID: {resolved_issue.id}")
    
    # Test the API endpoint directly
    try:
        # First, try to login (you might need to adjust credentials)
        login_data = {
            'username': 'admin',  # Adjust if needed
            'password': 'admin123'  # Adjust if needed
        }
        
        session = requests.Session()
        
        # Get CSRF token first
        csrf_response = session.get('http://127.0.0.1:8000/api/auth/user/')
        print(f"CSRF request status: {csrf_response.status_code}")
        
        # Try to login
        login_response = session.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            
            # Now try to generate report
            report_url = f'http://127.0.0.1:8000/api/issues/{resolved_issue.id}/generate_report/'
            print(f"Testing URL: {report_url}")
            
            report_response = session.post(report_url)
            print(f"Report generation status: {report_response.status_code}")
            
            if report_response.status_code == 200:
                print("✅ Report generation successful!")
                print(f"   Content type: {report_response.headers.get('content-type')}")
                print(f"   Content length: {len(report_response.content)} bytes")
                return True
            else:
                print(f"❌ Report generation failed!")
                print(f"   Response: {report_response.text}")
                return False
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        traceback.print_exc()
        return False

def test_direct_report_generation():
    """Test report generation directly in Python"""
    print("\n🐍 DIRECT PYTHON TEST")
    print("=" * 25)
    
    # Get a resolved issue
    resolved_issue = Issue.objects.filter(status='resolved').first()
    if not resolved_issue:
        print("❌ No resolved issue to test with")
        return False
    
    print(f"Testing with issue: {resolved_issue.auto_title}")
    
    try:
        generator = MaintenanceReportGenerator()
        pdf_content = generator.generate_pdf_report(resolved_issue)
        print(f"✅ Direct generation successful! Size: {len(pdf_content)} bytes")
        
        # Save test file
        test_file = os.path.join(settings.BASE_DIR, 'debug_test_report.pdf')
        with open(test_file, 'wb') as f:
            f.write(pdf_content)
        print(f"✅ Test file saved: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct generation failed: {e}")
        traceback.print_exc()
        return False

def check_browser_console():
    """Instructions for checking browser console"""
    print("\n🌐 BROWSER DEBUGGING INSTRUCTIONS")
    print("=" * 40)
    print("To debug the frontend issue:")
    print("1. Open your browser and go to the issue page")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the 'Console' tab")
    print("4. Click the 'Generate Report' button")
    print("5. Look for any error messages in red")
    print("6. Go to the 'Network' tab and check for failed requests")
    print("7. Look for the POST request to generate_report and check its response")

def main():
    print("🚀 COMPREHENSIVE REPORT GENERATION DEBUG")
    print("=" * 60)
    
    all_good = True
    
    # Step 1: Check if backend is running
    if not check_backend_logs():
        all_good = False
    
    # Step 2: Check permissions and users
    if not check_permissions_and_users():
        all_good = False
    
    # Step 3: Check resolved issues
    if not check_resolved_issues():
        all_good = False
    
    # Step 4: Test direct report generation
    if not test_direct_report_generation():
        all_good = False
    
    # Step 5: Test API endpoint
    if not test_api_endpoint():
        all_good = False
    
    # Step 6: Browser debugging instructions
    check_browser_console()
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 All backend tests passed! The issue might be in the frontend.")
        print("   Please check the browser console for JavaScript errors.")
    else:
        print("❌ Some backend issues found. Please fix them first.")
    
    print("\nNext steps:")
    print("1. Make sure Django backend is running")
    print("2. Make sure you have a user with Executive/Management/Admin role")
    print("3. Make sure you have at least one resolved issue")
    print("4. Check browser console for frontend errors")

if __name__ == '__main__':
    main() 