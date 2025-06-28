import sqlite3
import os

# Connect to the database
db_path = 'erabase_db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("All tables in erabase_db:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check for manufacturing tables specifically
    manufacturing_tables = [t[0] for t in tables if 'manufacturing' in t[0].lower()]
    print(f"\nManufacturing related tables: {manufacturing_tables}")
    
    # Show schema for manufacturing tables
    for table_name in manufacturing_tables:
        print(f"\nSchema for {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()
else:
    print(f"Database file {db_path} not found!") 