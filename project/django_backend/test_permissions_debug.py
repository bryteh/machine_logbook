#!/usr/bin/env python
"""
Debug script for permission issues
"""
import os
import sys
import django

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')

# Setup Django
django.setup()

from issues.models import PublicRole, Permission
from issues.permissions import IsPublicOrAuthenticated
from issues.views import RemedyViewSet
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_permission_class():
    """Test the IsPublicOrAuthenticated permission class directly"""
    print("🔍 Testing IsPublicOrAuthenticated Permission Class")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.post('/api/issues/test-id/remedies/', {})
    request.user = AnonymousUser()
    
    # Create a mock view
    view = RemedyViewSet()
    view.request = request
    view.action = 'create'
    
    # Test the permission
    permission_class = IsPublicOrAuthenticated()
    result = permission_class.has_permission(request, view)
    
    print(f"Permission check result: {result}")
    print(f"Request method: {request.method}")
    print(f"User type: {type(request.user)}")
    print(f"View class name: {view.__class__.__name__}")
    
    # Check public role permissions
    try:
        public_role = PublicRole.load()
        perms = list(public_role.permissions.values_list('codename', flat=True))
        print(f"Public permissions: {perms}")
        print(f"Has crud_remedies: {'crud_remedies' in perms}")
    except Exception as e:
        print(f"Error loading public role: {e}")
    
    return result

def test_remedy_creation_endpoint():
    """Test the actual remedy creation endpoint"""
    print("\n🔍 Testing Remedy Creation Endpoint")
    print("=" * 40)
    
    from django.test import Client
    from issues.models import Issue
    
    # Create a test issue first
    try:
        # Try to find an existing issue or create a test one
        issue = Issue.objects.first()
        if not issue:
            issue = Issue.objects.create(
                category='mechanical',
                priority='medium',
                machine_id_ref='TEST001',
                description='Test issue',
                reported_by='Test User'
            )
            print(f"✓ Created test issue: {issue.id}")
        else:
            print(f"✓ Using existing issue: {issue.id}")
        
        # Test API call
        client = Client()
        remedy_data = {
            'description': 'Test remedy',
            'technician_name': 'Test Tech',
            'is_external': False,
            'is_machine_runnable': True
        }
        
        response = client.post(
            f'/api/issues/{issue.id}/remedies/',
            data=remedy_data,
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Remedy creation works!")
            return True
        else:
            print("❌ FAILED: Remedy creation failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Debugging Permission Issues")
    print("=" * 60)
    
    test1_result = test_permission_class()
    test2_result = test_remedy_creation_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 Debug Results:")
    print(f"  1. Permission Class Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  2. Endpoint Test: {'✅ PASS' if test2_result else '❌ FAIL'}")

if __name__ == "__main__":
    main() 