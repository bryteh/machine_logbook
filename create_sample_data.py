import sqlite3
import os

# Connect to the erabase_db
db_path = '../../../erabase_db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add sample departments
departments = [
    ('DEPT001', 'CNC Machining', False, 85.50),
    ('DEPT002', 'Assembly Line', False, 90.25),
    ('DEPT003', 'Quality Control', False, 95.00),
    ('DEPT004', 'Packaging', True, 80.75)
]

# Add sample machines
machines = [
    ('MACH001', 'CNC-01', 'Haas VF-2', 'operational', 'DEPT001'),
    ('MACH002', 'CNC-02', 'Haas VF-3', 'operational', 'DEPT001'), 
    ('MACH003', 'CNC-03', 'Mazak VCN-414', 'maintenance', 'DEPT001'),
    ('MACH004', 'ASM-01', 'Assembly Station A', 'operational', 'DEPT002'),
    ('MACH005', 'ASM-02', 'Assembly Station B', 'operational', 'DEPT002'),
    ('MACH006', 'QC-01', 'CMM Zeiss', 'operational', 'DEPT003'),
    ('MACH007', 'PKG-01', 'Packaging Line 1', 'operational', 'DEPT004')
]

try:
    # Insert departments
    cursor.executemany(
        'INSERT OR REPLACE INTO manufacturing_department (department_id, name, is_subcontracted, efficiency_pct) VALUES (?, ?, ?, ?)', 
        departments
    )
    
    # Insert machines
    cursor.executemany(
        'INSERT OR REPLACE INTO manufacturing_machine (machine_id, machine_number, model, status, department_id) VALUES (?, ?, ?, ?, ?)', 
        machines
    )
    
    conn.commit()
    
    print("✅ Sample data added successfully!")
    print(f"Added {len(departments)} departments and {len(machines)} machines")
    
    # Verify the data
    cursor.execute('SELECT COUNT(*) FROM manufacturing_department')
    dept_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM manufacturing_machine')
    machine_count = cursor.fetchone()[0]
    
    print(f"Total departments in DB: {dept_count}")
    print(f"Total machines in DB: {machine_count}")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    
finally:
    conn.close() 