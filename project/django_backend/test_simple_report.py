#!/usr/bin/env python3
"""
Simple test for report generation without Accept header
"""

import requests
import json

def test_simple_report():
    """Test report generation without Accept header"""
    print("🔍 Testing Simple Report Generation")
    print("=" * 40)
    
    session = requests.Session()
    
    try:
        # Step 1: Get CSRF token
        print("1. Getting CSRF token...")
        csrf_response = session.get('http://127.0.0.1:8000/api/auth/csrf/')
        print(f"   CSRF request status: {csrf_response.status_code}")
        
        if csrf_response.status_code != 200:
            print("   ❌ Failed to get CSRF token")
            return False
        
        csrf_data = csrf_response.json()
        csrf_token = csrf_data.get('csrfToken')
        print(f"   ✅ CSRF token: {csrf_token[:10]}...")
        
        # Step 2: Login
        print("2. Logging in...")
        login_data = {'username': 'test_executive', 'password': 'testpass123'}
        login_response = session.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'X-CSRFToken': csrf_token}
        )
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
        
        print("   ✅ Login successful")
        
        # Step 3: Test report generation without Accept header
        print("3. Testing report generation (no Accept header)...")
        
        # Get a fresh CSRF token after login
        csrf_response2 = session.get('http://127.0.0.1:8000/api/auth/csrf/')
        csrf_token2 = csrf_response2.json().get('csrfToken')
        
        # Test with a resolved issue
        report_url = 'http://127.0.0.1:8000/api/issues/f314fc33-878c-42ae-acf5-c553552f43e3/generate_report/'
        
        report_response = session.post(
            report_url,
            headers={
                'X-CSRFToken': csrf_token2,
                # No Accept header
            }
        )
        
        print(f"   Report generation status: {report_response.status_code}")
        print(f"   Content type: {report_response.headers.get('content-type')}")
        
        if report_response.status_code == 200:
            print("   ✅ Report generation successful!")
            print(f"   Content length: {len(report_response.content)} bytes")
            
            # Save the PDF
            with open('test_report_simple.pdf', 'wb') as f:
                f.write(report_response.content)
            print("   ✅ PDF saved as: test_report_simple.pdf")
            
            return True
        else:
            print(f"   ❌ Report generation failed: {report_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def test_direct_url():
    """Test the URL directly"""
    print("\n🔍 Testing Direct URL Access")
    print("=" * 35)
    
    try:
        # Test if the URL exists
        response = requests.get('http://127.0.0.1:8000/api/issues/f314fc33-878c-42ae-acf5-c553552f43e3/generate_report/')
        print(f"GET request status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test POST without authentication
        response = requests.post('http://127.0.0.1:8000/api/issues/f314fc33-878c-42ae-acf5-c553552f43e3/generate_report/')
        print(f"POST request status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Direct URL test failed: {e}")

if __name__ == '__main__':
    print("🚀 SIMPLE REPORT TEST")
    print("=" * 25)
    
    test_direct_url()
    success = test_simple_report()
    
    print("\n" + "=" * 25)
    if success:
        print("🎉 Report generation works!")
    else:
        print("❌ Report generation failed.") 