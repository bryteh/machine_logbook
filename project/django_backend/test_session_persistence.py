#!/usr/bin/env python
import requests
import json

print("🔍 Testing Session Persistence")
print("=" * 40)

# Create a session to maintain cookies
session = requests.Session()

# Test 1: Login
print("1️⃣ Testing Login")
login_data = {'username': 'admin', 'password': 'admin123'}

try:
    response = session.post('http://127.0.0.1:8000/api/auth/login/', json=login_data)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful")
        print(f"Login Response: {response.json()}")
        print(f"Session Cookies: {dict(session.cookies)}")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Test 2: Get Current User (using same session)
print("\n2️⃣ Testing Get Current User")
try:
    response = session.get('http://127.0.0.1:8000/api/auth/user/')
    print(f"Get User Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Session maintained - getCurrentUser successful")
        print(f"User Data: {response.json()}")
    else:
        print(f"❌ Session lost - getCurrentUser failed: {response.text}")
        print("This is likely why login redirects back to login page!")
except Exception as e:
    print(f"❌ getCurrentUser error: {e}")

# Test 3: Check CSRF and session cookies
print("\n3️⃣ Cookie Analysis")
cookies = dict(session.cookies)
print(f"All cookies: {cookies}")

if 'sessionid' in cookies:
    print("✅ Session cookie present")
else:
    print("❌ Session cookie missing!")

if 'csrftoken' in cookies:
    print("✅ CSRF token present")
else:
    print("❌ CSRF token missing!")

print("\n" + "=" * 40)
print("Session persistence test complete") 