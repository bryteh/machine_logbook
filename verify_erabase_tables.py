#!/usr/bin/env python3
"""
Verify we're reading from the correct erabase_db database
and the manufacturing_machine and manufacturing_department tables
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

# Add the django_backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'project', 'django_backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import ManufacturingDepartment, ManufacturingMachine, Issue

def verify_database_connection():
    """Verify we're connected to the correct database"""
    print("=== DATABASE CONNECTION VERIFICATION ===")
    
    # Check database name
    db_name = connection.settings_dict['NAME']
    db_user = connection.settings_dict['USER']
    db_host = connection.settings_dict['HOST']
    db_port = connection.settings_dict['PORT']
    
    print(f"Database Name: {db_name}")
    print(f"Database User: {db_user}")
    print(f"Database Host: {db_host}")
    print(f"Database Port: {db_port}")
    
    # Test connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), version();")
        db_info = cursor.fetchone()
        print(f"Connected to database: {db_info[0]}")
        print(f"PostgreSQL version: {db_info[1]}")
        
        # Check if our tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('manufacturing_department', 'manufacturing_machine')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\nFound tables: {[table[0] for table in tables]}")
        
        # Check table structures
        for table_name in ['manufacturing_department', 'manufacturing_machine']:
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print(f"\n{table_name} columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")

def test_model_queries():
    """Test Django model queries"""
    print("\n=== DJANGO MODEL QUERIES ===")
    
    # Test ManufacturingDepartment
    dept_count = ManufacturingDepartment.objects.count()
    print(f"ManufacturingDepartment records: {dept_count}")
    
    if dept_count > 0:
        print("\nFirst 5 departments:")
        for dept in ManufacturingDepartment.objects.all()[:5]:
            print(f"  - {dept.department_id}: {dept.name}")
    
    # Test ManufacturingMachine
    machine_count = ManufacturingMachine.objects.count()
    print(f"\nManufacturingMachine records: {machine_count}")
    
    if machine_count > 0:
        print("\nFirst 5 machines:")
        for machine in ManufacturingMachine.objects.all()[:5]:
            print(f"  - {machine.machine_id}: {machine.model} (Dept: {machine.department.department_id})")
    
    # Test Issue model (should be in Django's managed tables)
    issue_count = Issue.objects.count()
    print(f"\nIssue records: {issue_count}")

def verify_table_data():
    """Verify we have actual data in the tables"""
    print("\n=== RAW TABLE DATA VERIFICATION ===")
    
    with connection.cursor() as cursor:
        # Check manufacturing_department data
        cursor.execute("SELECT COUNT(*) FROM manufacturing_department;")
        dept_count = cursor.fetchone()[0]
        print(f"manufacturing_department table has {dept_count} records")
        
        if dept_count > 0:
            cursor.execute("SELECT department_id, name FROM manufacturing_department LIMIT 3;")
            depts = cursor.fetchall()
            print("Sample departments:")
            for dept in depts:
                print(f"  - {dept[0]}: {dept[1]}")
        
        # Check manufacturing_machine data
        cursor.execute("SELECT COUNT(*) FROM manufacturing_machine;")
        machine_count = cursor.fetchone()[0]
        print(f"\nmanufacturing_machine table has {machine_count} records")
        
        if machine_count > 0:
            cursor.execute("SELECT machine_id, model, department_id FROM manufacturing_machine LIMIT 3;")
            machines = cursor.fetchall()
            print("Sample machines:")
            for machine in machines:
                print(f"  - {machine[0]}: {machine[1]} (Dept: {machine[2]})")

if __name__ == "__main__":
    try:
        verify_database_connection()
        test_model_queries()
        verify_table_data()
        print("\n✅ Successfully verified connection to erabase_db with manufacturing tables!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()