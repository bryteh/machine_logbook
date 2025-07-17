#!/usr/bin/env python3
"""
Check what database Django is currently connected to
"""

import os
import django
from django.conf import settings
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import ManufacturingDepartment, ManufacturingMachine

print("=== CURRENT DATABASE CONNECTION ===")
print(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
print(f"Database Name: {settings.DATABASES['default']['NAME']}")
print(f"Database User: {settings.DATABASES['default']['USER']}")
print(f"Database Host: {settings.DATABASES['default']['HOST']}")
print(f"Database Port: {settings.DATABASES['default']['PORT']}")

print("\n=== TESTING CONNECTION ===")
try:
    with connection.cursor() as cursor:
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            cursor.execute("SELECT current_database(), version();")
            result = cursor.fetchone()
            print(f"Connected to PostgreSQL database: {result[0]}")
            print(f"Version: {result[1]}")
        elif 'sqlite' in settings.DATABASES['default']['ENGINE']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Connected to SQLite database")
            print(f"Tables: {[t[0] for t in tables]}")
        
        # Test our models
        dept_count = ManufacturingDepartment.objects.count()
        machine_count = ManufacturingMachine.objects.count()
        
        print(f"\nManufacturingDepartment records: {dept_count}")
        print(f"ManufacturingMachine records: {machine_count}")
        
        if dept_count > 0:
            print("\nSample departments:")
            for dept in ManufacturingDepartment.objects.all()[:3]:
                print(f"  - {dept.department_id}: {dept.name}")
        
        if machine_count > 0:
            print("\nSample machines:")
            for machine in ManufacturingMachine.objects.all()[:3]:
                print(f"  - {machine.machine_id}: {machine.model}")
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()