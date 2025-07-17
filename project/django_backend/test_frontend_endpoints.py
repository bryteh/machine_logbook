#!/usr/bin/env python
"""
Test the exact endpoints the frontend is trying to use
"""
import requests
import json
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue

def test_frontend_remedy_endpoints():
    """Test the endpoints exactly as the frontend calls them"""
    print("🔍 Testing Frontend Remedy Endpoints")
    print("=" * 50)
    
    # Get an existing issue
    issue = Issue.objects.first()
    if not issue:
        print("❌ No issues found in database")
        return False
    
    print(f"✓ Using issue: {issue.id}")
    
    # Test 1: Frontend approach - /issues/{id}/add_remedy/
    print("\n1️⃣ Testing Frontend Endpoint: /issues/{id}/add_remedy/")
    url1 = f'http://localhost:8000/api/issues/{issue.id}/add_remedy/'
    remedy_data = {
        'description': 'Test remedy via add_remedy endpoint',
        'technician_name': 'Frontend Test Tech',
        'is_external': False,
        'is_machine_runnable': True
    }
    
    try:
        response1 = requests.post(url1, json=remedy_data)
        print(f"📊 Status: {response1.status_code}")
        
        if response1.status_code == 201:
            print("✅ SUCCESS: Frontend endpoint works!")
            try:
                print(f"📝 Response: {json.dumps(response1.json(), indent=2)}")
            except:
                print(f"📝 Response: {response1.text}")
        else:
            print("❌ FAILED: Frontend endpoint failed")
            try:
                print(f"📝 Error: {json.dumps(response1.json(), indent=2)}")
            except:
                print(f"📝 Error: {response1.text}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Alternative approach - /issues/{id}/remedies/ 
    print("\n2️⃣ Testing Alternative Endpoint: /issues/{id}/remedies/")
    url2 = f'http://localhost:8000/api/issues/{issue.id}/remedies/'
    
    try:
        response2 = requests.post(url2, json=remedy_data)
        print(f"📊 Status: {response2.status_code}")
        
        if response2.status_code == 201:
            print("✅ SUCCESS: Alternative endpoint works!")
            try:
                print(f"📝 Response: {json.dumps(response2.json(), indent=2)}")
            except:
                print(f"📝 Response: {response2.text}")
        else:
            print("❌ FAILED: Alternative endpoint failed")
            try:
                print(f"📝 Error: {json.dumps(response2.json(), indent=2)}")
            except:
                print(f"📝 Error: {response2.text}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    return True

def test_login_endpoint():
    """Test login exactly as frontend does"""
    print("\n🔍 Testing Frontend Login Endpoint")
    print("=" * 40)
    
    url = 'http://localhost:8000/api/auth/login/'
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(url, json=login_data)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Login endpoint works!")
            print(f"📝 Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print("❌ FAILED: Login endpoint failed")
            print(f"📝 Error: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Frontend API Endpoints")
    print("=" * 60)
    
    test1 = test_frontend_remedy_endpoints()
    test2 = test_login_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 Results:")
    print(f"  Remedy Endpoints: {'✅ TESTED' if test1 else '❌ FAILED'}")
    print(f"  Login Endpoint: {'✅ PASS' if test2 else '❌ FAIL'}") 