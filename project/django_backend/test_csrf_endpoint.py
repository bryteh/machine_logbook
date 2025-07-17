#!/usr/bin/env python3
"""
Test the new CSRF endpoint
"""

import requests
import json

def test_csrf_endpoint():
    """Test the CSRF token endpoint"""
    print("🔍 Testing CSRF Token Endpoint")
    print("=" * 35)
    
    try:
        # Test the new CSRF endpoint
        response = requests.get('http://127.0.0.1:8000/api/auth/csrf/')
        print(f"CSRF endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('csrfToken')
            print(f"✅ CSRF token received: {token[:10]}...")
            
            # Check if token is set in cookies
            csrf_cookie = None
            for cookie in response.cookies:
                if cookie.name == 'csrftoken':
                    csrf_cookie = cookie.value
                    break
            
            if csrf_cookie:
                print(f"✅ CSRF cookie set: {csrf_cookie[:10]}...")
            else:
                print("❌ No CSRF cookie found")
            
            return True
        else:
            print(f"❌ CSRF endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CSRF endpoint: {e}")
        return False

def test_report_generation_with_csrf():
    """Test report generation with proper CSRF handling"""
    print("\n🔍 Testing Report Generation with CSRF")
    print("=" * 45)
    
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
        
        # Step 3: Test report generation
        print("3. Testing report generation...")
        
        # Get a fresh CSRF token after login
        csrf_response2 = session.get('http://127.0.0.1:8000/api/auth/csrf/')
        csrf_token2 = csrf_response2.json().get('csrfToken')
        
        # Test with a resolved issue (using ID from previous debug)
        report_url = 'http://127.0.0.1:8000/api/issues/f314fc33-878c-42ae-acf5-c553552f43e3/generate_report/'
        
        report_response = session.post(
            report_url,
            headers={
                'X-CSRFToken': csrf_token2,
                'Accept': 'application/pdf'
            }
        )
        
        print(f"   Report generation status: {report_response.status_code}")
        
        if report_response.status_code == 200:
            print("   ✅ Report generation successful!")
            print(f"   Content type: {report_response.headers.get('content-type')}")
            print(f"   Content length: {len(report_response.content)} bytes")
            
            # Save the PDF
            with open('test_report_csrf_fix.pdf', 'wb') as f:
                f.write(report_response.content)
            print("   ✅ PDF saved as: test_report_csrf_fix.pdf")
            
            return True
        else:
            print(f"   ❌ Report generation failed: {report_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 CSRF TOKEN FIX TEST")
    print("=" * 30)
    
    success1 = test_csrf_endpoint()
    success2 = test_report_generation_with_csrf()
    
    print("\n" + "=" * 30)
    if success1 and success2:
        print("🎉 All tests passed! CSRF issue should be fixed.")
    else:
        print("❌ Some tests failed. Please check the errors above.") 