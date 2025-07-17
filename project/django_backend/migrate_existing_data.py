#!/usr/bin/env python
"""
Migrate existing database structure and data to Supabase
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path
import psycopg2
from decouple import config

class DatabaseMigrator:
    def __init__(self):
        # Source (local) database configuration
        self.source_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'erabase_db',
            'user': 'erabase_user',
            'password': '131313'  # Your local password
        }
        
        # Target (Supabase) database configuration
        self.target_config = {
            'host': 'db.spqxhiavpnajramwjacs.supabase.co',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres',
            'password': '23,JalanIstimewa4'  # Your Supabase password
        }
        
        self.temp_dir = tempfile.mkdtemp()
        print(f"📁 Using temporary directory: {self.temp_dir}")
    
    def test_connections(self):
        """Test both source and target database connections"""
        print("🔍 Testing database connections...")
        
        # Test source database
        try:
            conn = psycopg2.connect(**self.source_config)
            conn.close()
            print("✅ Source database (local) connection successful")
        except Exception as e:
            print(f"❌ Source database connection failed: {e}")
            return False
        
        # Test target database
        try:
            conn = psycopg2.connect(**self.target_config, sslmode='require')
            conn.close()
            print("✅ Target database (Supabase) connection successful")
        except Exception as e:
            print(f"❌ Target database connection failed: {e}")
            return False
        
        return True
    
    def dump_source_schema(self):
        """Dump schema from source database"""
        print("\n📊 Dumping database schema...")
        
        schema_file = os.path.join(self.temp_dir, 'schema.sql')
        
        # Use pg_dump to export schema only
        dump_cmd = [
            'pg_dump',
            f'--host={self.source_config["host"]}',
            f'--port={self.source_config["port"]}',
            f'--username={self.source_config["user"]}',
            f'--dbname={self.source_config["database"]}',
            '--schema-only',
            '--no-owner',
            '--no-privileges',
            '--file', schema_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.source_config['password']
        
        try:
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Schema dumped to: {schema_file}")
                return schema_file
            else:
                print(f"❌ Schema dump failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Schema dump error: {e}")
            return None
    
    def dump_source_data(self):
        """Dump data from source database"""
        print("\n💾 Dumping database data...")
        
        data_file = os.path.join(self.temp_dir, 'data.sql')
        
        # Use pg_dump to export data only
        dump_cmd = [
            'pg_dump',
            f'--host={self.source_config["host"]}',
            f'--port={self.source_config["port"]}',
            f'--username={self.source_config["user"]}',
            f'--dbname={self.source_config["database"]}',
            '--data-only',
            '--no-owner',
            '--no-privileges',
            '--disable-triggers',
            '--file', data_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.source_config['password']
        
        try:
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Data dumped to: {data_file}")
                return data_file
            else:
                print(f"❌ Data dump failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Data dump error: {e}")
            return None
    
    def clean_sql_file(self, sql_file):
        """Clean SQL file for Supabase compatibility"""
        print(f"\n🧹 Cleaning SQL file: {os.path.basename(sql_file)}")
        
        with open(sql_file, 'r') as f:
            content = f.read()
        
        # Remove problematic statements for Supabase
        replacements = [
            # Remove CREATE DATABASE statements
            ('CREATE DATABASE', '-- CREATE DATABASE'),
            # Remove CONNECT statements
            ('\\connect', '-- \\connect'),
            # Remove extension creation (Supabase handles these)
            ('CREATE EXTENSION', '-- CREATE EXTENSION'),
            # Remove role/user creation
            ('CREATE ROLE', '-- CREATE ROLE'),
            ('CREATE USER', '-- CREATE USER'),
            # Remove ownership changes
            ('ALTER TABLE', '-- ALTER TABLE'),
            ('OWNER TO', '-- OWNER TO'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Write cleaned content
        cleaned_file = sql_file.replace('.sql', '_cleaned.sql')
        with open(cleaned_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Cleaned SQL saved to: {cleaned_file}")
        return cleaned_file
    
    def restore_to_supabase(self, sql_file):
        """Restore SQL file to Supabase database"""
        print(f"\n🔄 Restoring to Supabase: {os.path.basename(sql_file)}")
        
        # Use psql to restore
        restore_cmd = [
            'psql',
            f'postgresql://{self.target_config["user"]}:{self.target_config["password"]}@{self.target_config["host"]}:{self.target_config["port"]}/{self.target_config["database"]}?sslmode=require',
            '-f', sql_file,
            '-v', 'ON_ERROR_STOP=1'
        ]
        
        try:
            result = subprocess.run(restore_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Restore successful")
                return True
            else:
                print(f"❌ Restore failed: {result.stderr}")
                print(f"📝 Output: {result.stdout}")
                return False
        except Exception as e:
            print(f"❌ Restore error: {e}")
            return False
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print("\n✅ Verifying migration...")
        
        try:
            conn = psycopg2.connect(**self.target_config, sslmode='require')
            cursor = conn.cursor()
            
            # Check for key tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('issues_issue', 'issues_remedy', 'issues_attachment', 'manufacturing_machine', 'manufacturing_department')
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"📊 Found {len(tables)} key tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count} records")
            
            conn.close()
            return len(tables) > 0
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def migrate_media_files(self):
        """Provide instructions for migrating media files"""
        print("\n📁 Media Files Migration")
        print("=" * 40)
        
        media_dir = Path("media")
        if media_dir.exists():
            print(f"📂 Found local media directory: {media_dir.absolute()}")
            
            # Count files
            image_files = list(media_dir.rglob("*.jpg")) + list(media_dir.rglob("*.png")) + list(media_dir.rglob("*.jpeg"))
            video_files = list(media_dir.rglob("*.mp4")) + list(media_dir.rglob("*.avi")) + list(media_dir.rglob("*.mov"))
            
            print(f"📸 Images: {len(image_files)} files")
            print(f"🎥 Videos: {len(video_files)} files")
            
            print("\n📝 Manual steps needed:")
            print("1. Set up Supabase Storage bucket:")
            print("   python supabase_utils.py")
            print("\n2. Upload files using Supabase dashboard or CLI")
            print("\n3. Update database records with new URLs")
        else:
            print("ℹ️  No local media directory found")
    
    def update_django_settings(self):
        """Provide instructions for updating Django settings"""
        print("\n⚙️  Django Configuration Update")
        print("=" * 40)
        
        print("📝 Update your .env file with these values:")
        print(f"""
# Database Configuration - Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=23,JalanIstimewa4
DB_HOST=db.spqxhiavpnajramwjacs.supabase.co
DB_PORT=5432

# You still need to get these from Supabase dashboard:
SUPABASE_URL=https://spqxhiavpnajramwjacs.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# For storage (get from Supabase Storage settings):
AWS_ACCESS_KEY_ID=your_supabase_access_key
AWS_SECRET_ACCESS_KEY=your_supabase_secret_key
AWS_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_S3_ENDPOINT_URL=https://spqxhiavpnajramwjacs.supabase.co/storage/v1/s3

# Enable Supabase storage
USE_S3=True
""")
        
        print("\n🔑 To get missing keys:")
        print("1. Go to your Supabase dashboard")
        print("2. Settings → API (for SUPABASE_ANON_KEY and SERVICE_ROLE_KEY)")
        print("3. Settings → Storage (for AWS access keys)")
    
    def migrate(self):
        """Run the complete migration process"""
        print("🚀 Starting Database Migration to Supabase")
        print("=" * 60)
        
        # Step 1: Test connections
        if not self.test_connections():
            print("❌ Connection test failed. Please check your database credentials.")
            return False
        
        # Step 2: Dump schema
        schema_file = self.dump_source_schema()
        if not schema_file:
            print("❌ Schema dump failed.")
            return False
        
        # Step 3: Clean schema file
        cleaned_schema = self.clean_sql_file(schema_file)
        
        # Step 4: Restore schema to Supabase
        if not self.restore_to_supabase(cleaned_schema):
            print("❌ Schema restore failed.")
            return False
        
        # Step 5: Dump data
        data_file = self.dump_source_data()
        if not data_file:
            print("❌ Data dump failed.")
            return False
        
        # Step 6: Clean data file
        cleaned_data = self.clean_sql_file(data_file)
        
        # Step 7: Restore data to Supabase
        if not self.restore_to_supabase(cleaned_data):
            print("❌ Data restore failed.")
            return False
        
        # Step 8: Verify migration
        if not self.verify_migration():
            print("❌ Migration verification failed.")
            return False
        
        # Step 9: Provide next steps
        self.migrate_media_files()
        self.update_django_settings()
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📝 Next Steps:")
        print("1. ✅ Update your .env file with Supabase credentials (see above)")
        print("2. ✅ Get missing API keys from Supabase dashboard")
        print("3. ✅ Set up Supabase Storage: python supabase_utils.py")
        print("4. ✅ Test your Django app: python manage.py runserver")
        print("5. ✅ Upload media files to Supabase Storage")
        print("6. ✅ Test file uploads through your application")
        
        print(f"\n🗂️  Migration files saved in: {self.temp_dir}")
        print("   Keep these files as backup until you verify everything works!")
        
        return True


def main():
    """Main migration function"""
    print("🔄 Database Migration Tool")
    print("This will migrate your existing database to Supabase")
    print()
    
    # Check if required tools are available
    required_tools = ['pg_dump', 'psql']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install PostgreSQL client tools first.")
        return
    
    # Confirm migration
    print("⚠️  This will:")
    print("   1. Export your local database structure and data")
    print("   2. Import everything to your Supabase database")
    print("   3. Preserve all your existing data")
    print()
    
    confirm = input("Do you want to continue? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    # Run migration
    migrator = DatabaseMigrator()
    success = migrator.migrate()
    
    if success:
        print(f"\n🌐 Your database is now on Supabase!")
        print(f"🔗 Connection: postgresql://postgres:***@db.spqxhiavpnajramwjacs.supabase.co:5432/postgres")
    else:
        print("\n❌ Migration failed. Please check the errors above.")


if __name__ == "__main__":
    main() 