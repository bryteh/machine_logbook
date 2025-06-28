import sqlite3

# Connect to the real erabase_db
conn = sqlite3.connect('erabase_db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
all_tables = cursor.fetchall()
print("All tables:", [t[0] for t in all_tables])

# Look for manufacturing tables
manufacturing_tables = [t[0] for t in all_tables if 'manufacturing' in t[0].lower()]
print("\nManufacturing tables:", manufacturing_tables)

# Check manufacturing_department data
if 'manufacturing_department' in [t[0] for t in all_tables]:
    print("\n=== manufacturing_department schema ===")
    cursor.execute('PRAGMA table_info(manufacturing_department);')
    columns = cursor.fetchall()
    for col in columns:
        pk_info = " (PRIMARY KEY)" if col[5] else ""
        print(f"  {col[1]}: {col[2]}{pk_info}")
    
    print("\n=== manufacturing_department data ===")
    cursor.execute('SELECT * FROM manufacturing_department;')
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

# Check manufacturing_machine data  
if 'manufacturing_machine' in [t[0] for t in all_tables]:
    print("\n=== manufacturing_machine schema ===")
    cursor.execute('PRAGMA table_info(manufacturing_machine);')
    columns = cursor.fetchall()
    for col in columns:
        pk_info = " (PRIMARY KEY)" if col[5] else ""
        print(f"  {col[1]}: {col[2]}{pk_info}")
    
    print("\n=== manufacturing_machine data (first 5) ===")
    cursor.execute('SELECT * FROM manufacturing_machine LIMIT 5;')
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

conn.close() 