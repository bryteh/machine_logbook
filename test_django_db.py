import os
import sys
import django

# Add the Django project to the path
sys.path.append('project/django_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def test_database_connection():
    try:
        print("Testing Django database connection to erabase_db...")
        
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_user, current_database(), version();")
            result = cursor.fetchone()
            
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"Connected as: {result[0]}")
            print(f"Database: {result[1]}")
            print(f"PostgreSQL version: {result[2][:50]}...")
            
            # Check for tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"\nFound {len(tables)} tables in the database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check for manufacturing-related tables
            manufacturing_tables = [t[0] for t in tables if 'manufacturing' in t[0].lower()]
            if manufacturing_tables:
                print(f"\nManufacturing tables found: {manufacturing_tables}")
                
                # Try to get some sample data
                for table in manufacturing_tables[:3]:  # Check first 3 tables
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count = cursor.fetchone()[0]
                        print(f"  {table}: {count} records")
                        
                        if count > 0 and count <= 10:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                            sample_data = cursor.fetchall()
                            print(f"    Sample data: {sample_data}")
                        elif count > 10:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
                            sample_data = cursor.fetchall()
                            print(f"    Sample data (first 2): {sample_data}")
                    except Exception as e:
                        print(f"  Error reading {table}: {e}")
            
            # Check for issues table specifically
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%issue%';
            """)
            issue_tables = cursor.fetchall()
            
            if issue_tables:
                print(f"\nIssue-related tables: {[t[0] for t in issue_tables]}")
                for table in issue_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                        count = cursor.fetchone()[0]
                        print(f"  {table[0]}: {count} records")
                    except Exception as e:
                        print(f"  Error reading {table[0]}: {e}")
        
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL server is not running")
        print("2. Database 'erabase_db' doesn't exist")
        print("3. User 'erabase_user' doesn't exist or wrong password")
        print("4. Django settings configuration issue")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)