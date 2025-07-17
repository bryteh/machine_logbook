#!/usr/bin/env python3
"""
Test CSRF token handling for report generation
"""

import os
import sys
import django
from django.conf import settings
import requests
import json

# Add the project path to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue
from django.contrib.auth.models import User
from issues.models import UserRole

def test_csrf_and_permissions():
    """Test CSRF token and permissions for report generation"""
    print("🔍 Testing CSRF and Permissions")
    print("=" * 40)
    
    # Get a resolved issue
    resolved_issue = Issue.objects.filter(status='resolved').first()
    if not resolved_issue:
        print("❌ No resolved issue found")
        return False
    
    print(f"Testing with issue: {resolved_issue.auto_title}")
    
    # Test with different users
    test_users = [
        ('admin', 'admin123'),
        ('test_executive', 'testpass123'),
        ('test_management', 'testpass123'),
    ]
    
    for username, password in test_users:
        print(f"\n--- Testing with user: {username} ---")
        
        session = requests.Session()
        
        try:
            # Step 1: Get CSRF token by hitting any GET endpoint
            print("1. Getting CSRF token...")
            csrf_response = session.get('http://127.0.0.1:8000/api/auth/user/')
            print(f"   CSRF request status: {csrf_response.status_code}")
            
            # Extract CSRF token from cookies
            csrf_token = None
            for cookie in session.cookies:
                if cookie.name == 'csrftoken':
                    csrf_token = cookie.value
                    break
            
            if csrf_token:
                print(f"   ✅ CSRF token obtained: {csrf_token[:10]}...")
            else:
                print("   ❌ No CSRF token found")
                continue
            
            # Step 2: Login
            print("2. Logging in...")
            login_data = {'username': username, 'password': password}
            login_response = session.post(
                'http://127.0.0.1:8000/api/auth/login/',
                json=login_data,
                headers={'X-CSRFToken': csrf_token}
            )
            print(f"   Login status: {login_response.status_code}")
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.text}")
                continue
            
            print("   ✅ Login successful")
            
            # Step 3: Test report generation
            print("3. Testing report generation...")
            report_url = f'http://127.0.0.1:8000/api/issues/{resolved_issue.id}/generate_report/'
            
            # Get fresh CSRF token after login
            csrf_response2 = session.get('http://127.0.0.1:8000/api/auth/user/')
            csrf_token2 = None
            for cookie in session.cookies:
                if cookie.name == 'csrftoken':
                    csrf_token2 = cookie.value
                    break
            
            report_response = session.post(
                report_url,
                headers={
                    'X-CSRFToken': csrf_token2 or csrf_token,
                    'Accept': 'application/pdf'
                }
            )
            
            print(f"   Report generation status: {report_response.status_code}")
            
            if report_response.status_code == 200:
                print(f"   ✅ Report generation successful!")
                print(f"   Content type: {report_response.headers.get('content-type')}")
                print(f"   Content length: {len(report_response.content)} bytes")
                
                # Save the PDF
                filename = f"test_report_{username}.pdf"
                with open(filename, 'wb') as f:
                    f.write(report_response.content)
                print(f"   ✅ PDF saved as: {filename}")
                
            elif report_response.status_code == 403:
                print(f"   ❌ Permission denied: {report_response.text}")
                
                # Check user permissions
                try:
                    user = User.objects.get(username=username)
                    if hasattr(user, 'role') and user.role:
                        print(f"   User role: {user.role.role.name}")
                        has_perm = user.role.has_permission('generate_reports')
                        print(f"   Can generate reports: {has_perm}")
                    else:
                        print(f"   ❌ User has no role assigned")
                except User.DoesNotExist:
                    print(f"   ❌ User {username} not found")
                
            elif report_response.status_code == 400:
                print(f"   ❌ Bad request: {report_response.text}")
            else:
                print(f"   ❌ Unexpected error: {report_response.text}")
            
        except Exception as e:
            print(f"   ❌ Test failed for {username}: {e}")
    
    return True

if __name__ == '__main__':
    test_csrf_and_permissions() 