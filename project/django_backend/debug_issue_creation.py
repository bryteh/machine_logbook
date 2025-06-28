#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import Issue, ManufacturingMachine, ManufacturingDepartment

def test_issue_creation():
    """Test issue creation to debug 400 error"""
    
    # Test data similar to what frontend sends
    test_data = {
        'category': 'mechanical',
        'priority': 'medium',
        'alarm_code': '101',
        'description': 'Test issue for debugging',
        'is_runnable': False,
        'machine_id_ref': 'SPOOL001',
        'reported_by': 'Test User'
    }
    
    print("Testing issue creation...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    # Test direct model creation
    try:
        print("\n1. Testing direct model creation...")
        issue = Issue.objects.create(**test_data)
        print(f"✅ Direct creation successful: {issue.id}")
        issue.delete()  # Clean up
    except Exception as e:
        print(f"❌ Direct creation failed: {e}")
        return
    
    # Test API creation
    try:
        print("\n2. Testing API creation...")
        response = requests.post(
            'http://127.0.0.1:8000/api/issues/',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ API creation successful")
        else:
            print("❌ API creation failed")
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
    
    # Check available machines
    print("\n3. Checking available machines...")
    machines = ManufacturingMachine.objects.all()[:5]
    for machine in machines:
        print(f"  - {machine.machine_id}: {machine.machine_number} ({machine.model})")
    
    # Check available departments
    print("\n4. Checking available departments...")
    departments = ManufacturingDepartment.objects.all()[:5]
    for dept in departments:
        print(f"  - {dept.department_id}: {dept.name}")

if __name__ == '__main__':
    test_issue_creation() 