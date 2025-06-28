import sqlite3

# Connect to the erabase_db
conn = sqlite3.connect('../../../erabase_db')
cursor = conn.cursor()

print("=== manufacturing_department schema ===")
cursor.execute('PRAGMA table_info(manufacturing_department);')
dept_columns = cursor.fetchall()
for col in dept_columns:
    pk_info = " (PRIMARY KEY)" if col[5] else ""
    print(f"  {col[1]}: {col[2]}{pk_info}")

print("\n=== manufacturing_machine schema ===")
cursor.execute('PRAGMA table_info(manufacturing_machine);')
machine_columns = cursor.fetchall()
for col in machine_columns:
    pk_info = " (PRIMARY KEY)" if col[5] else ""
    print(f"  {col[1]}: {col[2]}{pk_info}")

print("\n=== Sample data from manufacturing_department ===")
cursor.execute('SELECT * FROM manufacturing_department LIMIT 3;')
dept_data = cursor.fetchall()
for row in dept_data:
    print(f"  {row}")

print("\n=== Sample data from manufacturing_machine ===")
cursor.execute('SELECT * FROM manufacturing_machine LIMIT 3;')
machine_data = cursor.fetchall()
for row in machine_data:
    print(f"  {row}")

conn.close() 