#!/usr/bin/env python
"""
Test Django setup and database connection
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import ManufacturingDepartment, ManufacturingMachine, Issue

def test_database_connection():
    print("=== Testing Database Connection ===")
    
    try:
        # Test department query
        print("\n1. Testing ManufacturingDepartment:")
        departments = ManufacturingDepartment.objects.all()[:5]
        print(f"   Found {departments.count()} departments")
        for dept in departments:
            print(f"   - {dept.department_id}: {dept.name}")
        
        # Test machine query
        print("\n2. Testing ManufacturingMachine:")
        machines = ManufacturingMachine.objects.all()[:5]
        print(f"   Found {machines.count()} machines")
        for machine in machines:
            print(f"   - {machine.machine_id}: {machine.machine_number} ({machine.model})")
            print(f"     Department: {machine.department.name}")
        
        # Test issue query (should be empty initially)
        print("\n3. Testing Issue:")
        issues = Issue.objects.all()
        print(f"   Found {issues.count()} issues")
        
        print("\n✅ Database connection working correctly!")
        print("   You can now start the Django server with: python manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_database_connection() 