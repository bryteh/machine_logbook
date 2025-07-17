#!/usr/bin/env python
"""
Direct API test for debugging authentication issues
"""
import os
import sys
import django
import requests
import json

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')

# Setup Django
django.setup()

from issues.models import Issue, PublicRole

def test_public_remedy_creation():
    """Test creating a remedy as a public user via API"""
    print("🔍 Testing Public Remedy Creation via API")
    print("=" * 50)
    
    # Get or create a test issue
    issue = Issue.objects.first()
    if not issue:
        issue = Issue.objects.create(
            category='mechanical',
            priority='medium',
            machine_id_ref='TEST001',
            description='Test issue for public remedy',
            reported_by='Test User'
        )
        print(f"✓ Created test issue: {issue.id}")
    else:
        print(f"✓ Using existing issue: {issue.id}")

    # Test remedy creation without authentication
    url = f'http://localhost:8000/api/issues/{issue.id}/remedies/'
    remedy_data = {
        'description': 'Test remedy from public user',
        'technician_name': 'Public Tech',
        'is_external': False,
        'is_machine_runnable': True
    }
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        print(f"📡 Making POST request to: {url}")
        print(f"📝 Data: {json.dumps(remedy_data, indent=2)}")
        
        response = requests.post(url, json=remedy_data, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📝 Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📝 Response Text: {response.text[:500]}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Public remedy creation works!")
            return True
        else:
            print("❌ FAILED: Public remedy creation failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to Django server")
        print("   Please make sure Django is running with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_public_role_setup():
    """Test if public role is set up correctly"""
    print("\n🔍 Testing Public Role Setup")
    print("=" * 40)
    
    try:
        public_role = PublicRole.load()
        permissions = list(public_role.permissions.values_list('codename', flat=True))
        print(f"✓ Public role found")
        print(f"📋 Permissions: {permissions}")
        
        if 'crud_remedies' in permissions:
            print("✅ crud_remedies permission found")
            return True
        else:
            print("❌ crud_remedies permission missing")
            return False
            
    except Exception as e:
        print(f"❌ Error loading public role: {e}")
        return False

def test_login_functionality():
    """Test login functionality"""
    print("\n🔍 Testing Login Functionality")
    print("=" * 40)
    
    # Try to find a user to test with
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get admin user or create one
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("No admin user found, creating one...")
            user = User.objects.create_superuser(
                username='testadmin',
                email='test@example.com',
                password='testpass123'
            )
            print(f"✓ Created admin user: {user.username}")
        else:
            print(f"✓ Using existing admin user: {user.username}")
        
        # Try to login
        url = 'http://localhost:8000/api/auth/login/'
        login_data = {
            'username': user.username,
            'password': 'testpass123' if not user.username == 'testadmin' else 'testpass123'
        }
        
        response = requests.post(url, json=login_data)
        print(f"📊 Login Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📝 Login Response: {json.dumps(response_json, indent=2)}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Login works!")
                return True
            else:
                print("❌ FAILED: Login failed")
                return False
        except:
            print(f"📝 Login Response Text: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Direct API Testing for Authentication Issues")
    print("=" * 60)
    
    test1 = test_public_role_setup()
    test2 = test_public_remedy_creation()
    test3 = test_login_functionality()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"  1. Public Role Setup: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  2. Public Remedy Creation: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  3. Login Functionality: {'✅ PASS' if test3 else '❌ FAIL'}")

if __name__ == "__main__":
    main()