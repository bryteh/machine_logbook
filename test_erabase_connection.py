import psycopg2
import sys

def test_erabase_connection():
    try:
        print("Testing connection to erabase_db with provided credentials...")
        
        # Your specific credentials
        conn = psycopg2.connect(
            host="localhost",
            database="erabase_db",
            user="erabase_user",
            password="131313",
            port=5432
        )
        
        print("✅ Successfully connected to PostgreSQL!")
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database(), version();")
        result = cursor.fetchone()
        
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
            for table in manufacturing_tables[:2]:  # Check first 2 tables
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} records")
                    
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                        sample_data = cursor.fetchall()
                        print(f"    Sample data: {sample_data}")
                except Exception as e:
                    print(f"  Error reading {table}: {e}")
        
        cursor.close()
        conn.close()
        print("\n✅ Connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL server is not running")
        print("2. Database 'erabase_db' doesn't exist")
        print("3. User 'erabase_user' doesn't exist or wrong password")
        print("4. Connection settings (host/port) are incorrect")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_erabase_connection()
    sys.exit(0 if success else 1)