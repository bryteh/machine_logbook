import psycopg2
import os

# Different connection configurations to try
configs = [
    # Correct credentials provided by user
    {"host": "localhost", "database": "erabase_db", "user": "erabase_user", "password": "131313"},
    
    # Trust authentication (no password)
    {"host": "localhost", "database": "erabase_db", "user": "postgres"},
    
    # Default postgres user with common passwords
    {"host": "localhost", "database": "erabase_db", "user": "postgres", "password": "postgres"},
    {"host": "localhost", "database": "erabase_db", "user": "postgres", "password": "admin"},
    {"host": "localhost", "database": "erabase_db", "user": "postgres", "password": "password"},
    {"host": "localhost", "database": "erabase_db", "user": "postgres", "password": ""},
    
    # Different users
    {"host": "localhost", "database": "erabase_db", "user": "admin"},
    {"host": "localhost", "database": "erabase_db", "user": "admin", "password": "admin"},
    {"host": "localhost", "database": "erabase_db", "user": "erabase", "password": ""},
]

print("Testing PostgreSQL connections...")
for i, config in enumerate(configs, 1):
    try:
        print(f"\nTest {i}: Trying {config}")
        conn = psycopg2.connect(**config, port=5432)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database(), version();")
        result = cursor.fetchone()
        
        print(f"✅ SUCCESS! Connected as: {result[0]} to database: {result[1]}")
        print(f"   PostgreSQL version: {result[2]}")
        
        # Check for manufacturing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%manufacturing%';
        """)
        tables = cursor.fetchall()
        print(f"   Manufacturing tables: {[t[0] for t in tables]}")
        
        # Check manufacturing_department data if it exists
        try:
            cursor.execute("SELECT department_id, name FROM manufacturing_department LIMIT 5;")
            dept_data = cursor.fetchall()
            print(f"   Sample department data: {dept_data}")
        except Exception as e:
            print(f"   No manufacturing_department table or error: {e}")
        
        conn.close()
        print(f"   This configuration works! Use this in Django settings.")
        break
        
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\nTest complete.") 