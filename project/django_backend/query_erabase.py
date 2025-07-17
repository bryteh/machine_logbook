#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.db import connection
from issues.models import ManufacturingDepartment, ManufacturingMachine, Issue

def query_erabase_data():
    print("=" * 60)
    print("QUERYING ERABASE_DB DATA")
    print("=" * 60)
    
    try:
        # Test raw database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_user, current_database(), version();")
            result = cursor.fetchone()
            print(f"✅ Connected to PostgreSQL as: {result[0]}")
            print(f"✅ Database: {result[1]}")
            print(f"✅ Version: {result[2][:50]}...")
            print()
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
            print()
        
        # Query Manufacturing Departments
        print("🏭 MANUFACTURING DEPARTMENTS:")
        departments = ManufacturingDepartment.objects.all()
        print(f"   Total: {departments.count()} departments")
        for dept in departments:
            print(f"   - {dept.department_id}: {dept.name} (Efficiency: {dept.efficiency_pct}%)")
        print()
        
        # Query Manufacturing Machines
        print("🔧 MANUFACTURING MACHINES:")
        machines = ManufacturingMachine.objects.all()
        print(f"   Total: {machines.count()} machines")
        for machine in machines[:10]:  # Show first 10
            print(f"   - {machine.machine_id}: {machine.name} ({machine.model}) - {machine.status}")
        if machines.count() > 10:
            print(f"   ... and {machines.count() - 10} more machines")
        print()
        
        # Query Issues
        print("🚨 MAINTENANCE ISSUES:")
        issues = Issue.objects.all()
        print(f"   Total: {issues.count()} issues")
        
        if issues.count() > 0:
            # Show recent issues
            recent_issues = issues.order_by('-created_at')[:5]
            print("   Recent issues:")
            for issue in recent_issues:
                print(f"   - {issue.title} ({issue.priority}) - {issue.status}")
                print(f"     Machine: {issue.machine.name if issue.machine else 'N/A'}")
                print(f"     Created: {issue.created_at.strftime('%Y-%m-%d %H:%M')}")
                print()
        
        # Department breakdown
        print("📊 DEPARTMENT BREAKDOWN:")
        for dept in departments:
            dept_machines = machines.filter(department=dept)
            dept_issues = issues.filter(machine__department=dept)
            print(f"   {dept.name}:")
            print(f"     - Machines: {dept_machines.count()}")
            print(f"     - Issues: {dept_issues.count()}")
            if dept_issues.count() > 0:
                open_issues = dept_issues.filter(status='open').count()
                print(f"     - Open Issues: {open_issues}")
        print()
        
        # Raw data sample
        print("📋 RAW DATA SAMPLES:")
        with connection.cursor() as cursor:
            # Sample from manufacturing_department
            cursor.execute("SELECT * FROM issues_manufacturingdepartment LIMIT 3;")
            dept_data = cursor.fetchall()
            if dept_data:
                print("   Manufacturing Departments (sample):")
                for row in dept_data:
                    print(f"     {row}")
            
            # Sample from manufacturing_machine
            cursor.execute("SELECT * FROM issues_manufacturingmachine LIMIT 3;")
            machine_data = cursor.fetchall()
            if machine_data:
                print("   Manufacturing Machines (sample):")
                for row in machine_data:
                    print(f"     {row}")
        
        print("\n✅ Successfully queried erabase_db data!")
        return True
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = query_erabase_data()
    sys.exit(0 if success else 1)