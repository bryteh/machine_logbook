#!/usr/bin/env python
"""
Database setup script for Machine Logbook Django backend.
This script helps ensure the existing PostgreSQL database is compatible with Django.
"""

import os
import sys


def main():
    """Main setup function"""
    print("🔧 Setting up Machine Logbook Database...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
    
    try:
        import django
        django.setup()
        
        from django.db import connection
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        
        # Check if manufacturing tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'manufacturing_machine'
                );
            """)
            machine_exists = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'manufacturing_department'
                );
            """)
            department_exists = cursor.fetchone()[0]
        
        # Create tables if they don't exist
        if not machine_exists:
            print("⚠️  manufacturing_machine table not found - creating it...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE manufacturing_machine (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(255) NOT NULL,
                        model_number VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
        else:
            print("✓ manufacturing_machine table exists")
            
        if not department_exists:
            print("⚠️  manufacturing_department table not found - creating it...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE manufacturing_department (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
        else:
            print("✓ manufacturing_department table exists")
        
        # Create sample data if tables are empty
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM manufacturing_department")
            dept_count = cursor.fetchone()[0]
            
            if dept_count == 0:
                print("📝 Creating sample departments...")
                departments = [
                    'CNC Machining',
                    'Assembly', 
                    'Quality Control',
                    'Finishing'
                ]
                for dept_name in departments:
                    cursor.execute(
                        "INSERT INTO manufacturing_department (name) VALUES (%s)",
                        [dept_name]
                    )
            
            cursor.execute("SELECT COUNT(*) FROM manufacturing_machine")
            machine_count = cursor.fetchone()[0]
            
            if machine_count == 0:
                print("📝 Creating sample machines...")
                machines = [
                    ('CNC Mill #1', 'Haas VF-2'),
                    ('CNC Mill #2', 'Haas VF-3'),
                    ('CNC Lathe #1', 'Haas ST-20'),
                    ('CNC Lathe #2', 'Haas ST-30'),
                    ('EDM Machine', 'Mitsubishi EA12'),
                    ('Surface Grinder', 'Okamoto ACC-124DX'),
                ]
                for name, model in machines:
                    cursor.execute(
                        "INSERT INTO manufacturing_machine (name, model_number) VALUES (%s, %s)",
                        [name, model]
                    )
        
        print("\n🎉 Database setup complete!")
        print("\nNext steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createsuperuser (optional)")
        print("4. Run: python manage.py runserver 8000")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 