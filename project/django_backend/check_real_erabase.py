import sqlite3
import os

# Check the main erabase_db file (the larger one)
db_path = '../../../../erabase_db'
print(f"Checking database: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nAll tables in main erabase_db: {[t[0] for t in tables]}")
        
        # Look for manufacturing related tables
        manufacturing_tables = [t[0] for t in tables if 'manufacturing' in t[0].lower()]
        print(f"Manufacturing tables: {manufacturing_tables}")
        
        # Check if the tables from the screenshot exist
        for table_name in manufacturing_tables:
            if 'department' in table_name.lower():
                print(f"\n=== {table_name} data ===")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Database file not found!") 