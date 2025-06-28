#!/usr/bin/env python
"""
Django sample data creation script
Run this with: python create_sample_data.py
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import ManufacturingDepartment, ManufacturingMachine, Issue

def create_sample_data():
    print("Creating sample data...")
    
    # Create departments
    departments = [
        {'department_id': 1, 'name': 'CNC Machining', 'description': 'Computer Numerical Control machining operations'},
        {'department_id': 2, 'name': 'Assembly', 'description': 'Product assembly and integration'},
        {'department_id': 3, 'name': 'Quality Control', 'description': 'Quality testing and inspection'},
        {'department_id': 4, 'name': 'Maintenance', 'description': 'Equipment maintenance and repair'},
    ]
    
    dept_objects = []
    for dept_data in departments:
        dept, created = ManufacturingDepartment.objects.get_or_create(
            department_id=dept_data['department_id'],
            defaults={
                'name': dept_data['name'],
                'description': dept_data['description']
            }
        )
        dept_objects.append(dept)
        if created:
            print(f"Created department: {dept.name}")
    
    # Create machines
    machines = [
        {
            'machine_id': 'CNC-001',
            'name': 'Haas VF-2',
            'department': dept_objects[0],  # CNC Machining
            'model': 'VF-2',
            'manufacturer': 'Haas Automation',
            'year_installed': 2020,
            'status': 'active'
        },
        {
            'machine_id': 'CNC-002', 
            'name': 'Haas VF-4',
            'department': dept_objects[0],  # CNC Machining
            'model': 'VF-4',
            'manufacturer': 'Haas Automation',
            'year_installed': 2019,
            'status': 'active'
        },
        {
            'machine_id': 'ASM-001',
            'name': 'Assembly Station 1',
            'department': dept_objects[1],  # Assembly
            'model': 'AS-1000',
            'manufacturer': 'Custom Built',
            'year_installed': 2021,
            'status': 'active'
        },
        {
            'machine_id': 'QC-001',
            'name': 'CMM Coordinate Measuring Machine',
            'department': dept_objects[2],  # Quality Control
            'model': 'CMM-500',
            'manufacturer': 'Zeiss',
            'year_installed': 2022,
            'status': 'active'
        },
    ]
    
    machine_objects = []
    for machine_data in machines:
        machine, created = ManufacturingMachine.objects.get_or_create(
            machine_id=machine_data['machine_id'],
            defaults=machine_data
        )
        machine_objects.append(machine)
        if created:
            print(f"Created machine: {machine.name}")
    
    # Create sample issues
    issues_data = [
        {
            'machine': machine_objects[0],  # Haas VF-2
            'title': 'Spindle overheating alarm',
            'description': 'Machine displayed alarm code 301 - spindle temperature exceeded maximum threshold during high-speed operation',
            'priority': 'high',
            'status': 'resolved',
            'created_at': datetime.now() - timedelta(days=5),
            'resolved_at': datetime.now() - timedelta(days=3),
            'downtime_minutes': 180,
        },
        {
            'machine': machine_objects[0],  # Haas VF-2
            'title': 'Tool changer malfunction',
            'description': 'Tool changer failed to select proper tool, causing program stoppage',
            'priority': 'medium',
            'status': 'in_progress',
            'created_at': datetime.now() - timedelta(days=2),
            'downtime_minutes': 45,
        },
        {
            'machine': machine_objects[1],  # Haas VF-4
            'title': 'Coolant leak detected',
            'description': 'Small coolant leak observed under machine base, requires investigation and repair',
            'priority': 'low',
            'status': 'open',
            'created_at': datetime.now() - timedelta(days=1),
            'downtime_minutes': 0,
        },
        {
            'machine': machine_objects[2],  # Assembly Station
            'title': 'Pneumatic pressure low',
            'description': 'Air pressure dropped below required 90 PSI threshold, affecting assembly operations',
            'priority': 'high',
            'status': 'resolved',
            'created_at': datetime.now() - timedelta(days=7),
            'resolved_at': datetime.now() - timedelta(days=6),
            'downtime_minutes': 120,
        },
    ]
    
    for issue_data in issues_data:
        issue, created = Issue.objects.get_or_create(
            title=issue_data['title'],
            machine=issue_data['machine'],
            defaults=issue_data
        )
        if created:
            print(f"Created issue: {issue.title}")
    
    print(f"\nSample data creation complete!")
    print(f"Departments: {ManufacturingDepartment.objects.count()}")
    print(f"Machines: {ManufacturingMachine.objects.count()}")
    print(f"Issues: {Issue.objects.count()}")

if __name__ == '__main__':
    create_sample_data() 