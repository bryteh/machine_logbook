#!/usr/bin/env python3
"""
List machine_id and department_id from erabase_db
"""

import os
import sys
import django

# Add the django_backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'project', 'django_backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import ManufacturingMachine
from django.db import connection

def list_machines():
    """List machine_id and department_id from manufacturing_machine table"""
    print("=== MACHINE LIST FROM ERABASE_DB ===")
    print("machine_id\t\tdepartment_id")
    print("-" * 40)
    
    try:
        # Using Django ORM
        machines = ManufacturingMachine.objects.all()[:10]
        
        if machines:
            for machine in machines:
                print(f"{machine.machine_id}\t\t{machine.department.department_id}")
        else:
            print("No machines found in the database.")
            
        print(f"\nTotal machines shown: {len(machines)}")
        
        # Also show raw SQL query result for verification
        print("\n=== RAW SQL VERIFICATION ===")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT machine_id, department_id 
                FROM manufacturing_machine 
                LIMIT 10;
            """)
            rows = cursor.fetchall()
            
            print("machine_id\t\tdepartment_id")
            print("-" * 40)
            for row in rows:
                print(f"{row[0]}\t\t{row[1]}")
                
            print(f"\nTotal rows from raw SQL: {len(rows)}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_machines()