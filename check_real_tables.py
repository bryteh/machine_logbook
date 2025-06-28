import psycopg2
import sys

def check_table_structure():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            database="erabase_db", 
            user="erabase_user",
            password="131313",
            port=5432
        )
        cursor = conn.cursor()
        
        print("=== MANUFACTURING_DEPARTMENT TABLE STRUCTURE ===")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'manufacturing_department' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        dept_columns = cursor.fetchall()
        
        for col in dept_columns:
            print(f"  {col[0]:<20} | {col[1]:<15} | Nullable: {col[2]:<3} | Max Length: {col[4] or 'N/A'}")
        
        print(f"\n=== SAMPLE DEPARTMENT DATA ===")
        cursor.execute("SELECT * FROM manufacturing_department LIMIT 5;")
        dept_data = cursor.fetchall()
        for row in dept_data:
            print(f"  {row}")
        
        print(f"\n=== MANUFACTURING_MACHINE TABLE STRUCTURE ===")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'manufacturing_machine' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        machine_columns = cursor.fetchall()
        
        for col in machine_columns:
            print(f"  {col[0]:<20} | {col[1]:<15} | Nullable: {col[2]:<3} | Max Length: {col[4] or 'N/A'}")
        
        print(f"\n=== SAMPLE MACHINE DATA ===")
        cursor.execute("SELECT * FROM manufacturing_machine LIMIT 5;")
        machine_data = cursor.fetchall()
        for row in machine_data:
            print(f"  {row}")
        
        # Check for any foreign key relationships
        print(f"\n=== FOREIGN KEY CONSTRAINTS ===")
        cursor.execute("""
            SELECT tc.table_name, kcu.column_name, 
                   ccu.table_name AS foreign_table_name,
                   ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND (tc.table_name='manufacturing_machine' OR tc.table_name='manufacturing_department');
        """)
        fk_constraints = cursor.fetchall()
        
        for fk in fk_constraints:
            print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    check_table_structure() 