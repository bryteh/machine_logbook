#!/usr/bin/env python
"""
Test database connection to erabase_db
"""
import psycopg2
import getpass

def test_connection(password):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="erabase_db", 
            user="postgres",
            password=password,
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT current_database(), version();")
        db_name, version = cur.fetchone()
        
        print(f"✅ SUCCESS! Connected to database: {db_name}")
        print(f"PostgreSQL version: {version}")
        
        # Check for existing tables
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('manufacturing_machine', 'manufacturing_department')
            ORDER BY table_name;
        """)
        
        existing_tables = cur.fetchall()
        if existing_tables:
            print(f"✅ Found existing tables: {[t[0] for t in existing_tables]}")
        else:
            print("⚠️  No manufacturing tables found - we'll create them")
            
        cur.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("❌ Wrong password")
        elif "database" in str(e) and "does not exist" in str(e):
            print("❌ Database 'erabase_db' does not exist")
        else:
            print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔍 Testing connection to erabase_db...")
    
    # Common passwords to try
    common_passwords = ["", "postgres", "admin", "password", "123456"]
    
    print("\n1️⃣  Trying common passwords...")
    for pwd in common_passwords:
        print(f"Trying password: {'(empty)' if pwd == '' else pwd}")
        if test_connection(pwd):
            print(f"\n🎉 Found working password: {'(empty)' if pwd == '' else pwd}")
            
            # Create .env file
            env_content = f"""# Database Configuration - Connect to existing erabase_db
DB_NAME=erabase_db
DB_USER=postgres
DB_PASSWORD={pwd}
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration (optional)
OPENAI_API_KEY=

# Media Configuration
MEDIA_ROOT=media/
MEDIA_URL=/media/"""
            
            print(f"\n📝 Creating .env file with working credentials...")
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ .env file created successfully!")
            return True
    
    print("\n2️⃣  None of the common passwords worked.")
    print("Please enter your PostgreSQL password manually:")
    
    while True:
        password = getpass.getpass("PostgreSQL password for 'postgres' user: ")
        if test_connection(password):
            print(f"\n🎉 Password works!")
            
            # Create .env file
            env_content = f"""# Database Configuration - Connect to existing erabase_db
DB_NAME=erabase_db
DB_USER=postgres
DB_PASSWORD={password}
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration (optional)
OPENAI_API_KEY=

# Media Configuration
MEDIA_ROOT=media/
MEDIA_URL=/media/"""
            
            print(f"\n📝 Creating .env file...")
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ .env file created successfully!")
            return True
        else:
            retry = input("Try again? (y/n): ")
            if retry.lower() != 'y':
                break
    
    print("\n❌ Could not establish database connection.")
    print("Please check:")
    print("1. PostgreSQL is running")
    print("2. Database 'erabase_db' exists") 
    print("3. User 'postgres' has access")

if __name__ == "__main__":
    main() 