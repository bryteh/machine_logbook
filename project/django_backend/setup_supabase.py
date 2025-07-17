#!/usr/bin/env python
"""
Complete Supabase Setup Script - Deploy Machine Maintenance Logbook
"""
import os
import sys
import subprocess
import tempfile
import psycopg2
from pathlib import Path

class SupabaseSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.env_file = self.project_dir / '.env'
        self.credentials = {}
        
    def welcome(self):
        """Welcome message and overview"""
        print("🚀 SUPABASE DEPLOYMENT SETUP")
        print("=" * 50)
        print()
        print("This script will help you deploy your Machine Maintenance Logbook to Supabase.")
        print()
        print("📋 What we'll do:")
        print("   1. ✅ Collect your Supabase credentials")
        print("   2. ✅ Create environment configuration")
        print("   3. ✅ Test connections")
        print("   4. ✅ Migrate your database")
        print("   5. ✅ Set up file storage")
        print("   6. ✅ Deploy your application")
        print()
        print("⏱️  Estimated time: 10-15 minutes")
        print()
        
        ready = input("Are you ready to start? (yes/no): ").lower().strip()
        if ready not in ['yes', 'y']:
            print("Setup cancelled. Run this script again when you're ready!")
            sys.exit(0)
    
    def collect_credentials(self):
        """Guide user through collecting Supabase credentials"""
        print("\n🔑 STEP 1: COLLECT SUPABASE CREDENTIALS")
        print("=" * 50)
        print()
        print("First, let's get your Supabase project credentials.")
        print("You'll need to copy these from your Supabase dashboard.")
        print()
        
        # Project basics
        print("📍 FROM YOUR SUPABASE DASHBOARD:")
        print("   Go to: https://supabase.com/dashboard/projects")
        print("   Click on your project")
        print()
        
        project_url = input("🔗 Enter your Project URL (https://xyz.supabase.co): ").strip()
        if not project_url.startswith('https://'):
            project_url = f"https://{project_url}"
        if not project_url.endswith('.supabase.co'):
            project_url = f"{project_url}.supabase.co"
        
        # Extract project ID
        project_id = project_url.replace('https://', '').replace('.supabase.co', '')
        
        print()
        print("🔑 API KEYS (Settings → API):")
        anon_key = input("   📝 Anon/Public Key: ").strip()
        service_key = input("   📝 Service Role Key: ").strip()
        
        print()
        print("🗄️  DATABASE (Settings → Database):")
        db_password = input("   📝 Database Password: ").strip()
        
        print()
        print("📦 STORAGE (Settings → Storage):")
        print("   If you don't have storage keys, click 'Generate access keys' first")
        storage_access_key = input("   📝 Access Key ID: ").strip()
        storage_secret_key = input("   📝 Secret Access Key: ").strip()
        
        print()
        print("🔧 OPTIONAL:")
        openai_key = input("   📝 OpenAI API Key (press Enter to skip): ").strip()
        
        # Store credentials
        self.credentials = {
            'project_id': project_id,
            'project_url': project_url,
            'anon_key': anon_key,
            'service_key': service_key,
            'db_password': db_password,
            'storage_access_key': storage_access_key,
            'storage_secret_key': storage_secret_key,
            'openai_key': openai_key,
        }
        
        print(f"\n✅ Credentials collected for project: {project_id}")
    
    def create_env_file(self):
        """Create .env file with collected credentials"""
        print("\n💾 STEP 2: CREATE ENVIRONMENT FILE")
        print("=" * 50)
        
        env_content = f"""# Database Configuration - Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD={self.credentials['db_password']}
DB_HOST=db.{self.credentials['project_id']}.supabase.co
DB_PORT=5432

# Supabase Configuration
SUPABASE_URL={self.credentials['project_url']}
SUPABASE_ANON_KEY={self.credentials['anon_key']}
SUPABASE_SERVICE_ROLE_KEY={self.credentials['service_key']}

# Supabase Storage Configuration
SUPABASE_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_ACCESS_KEY_ID={self.credentials['storage_access_key']}
AWS_SECRET_ACCESS_KEY={self.credentials['storage_secret_key']}
AWS_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_S3_ENDPOINT_URL={self.credentials['project_url']}/storage/v1/s3
AWS_S3_REGION_NAME=us-east-1
AWS_DEFAULT_ACL=public-read

# Django Configuration
SECRET_KEY=django-supabase-{self.credentials['project_id']}-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration
OPENAI_API_KEY={self.credentials['openai_key']}

# Media Configuration
MEDIA_URL={self.credentials['project_url']}/storage/v1/object/public/machine-maintenance-media/
USE_S3=True
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            print(f"✅ Created .env file: {self.env_file}")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
        
        return True
    
    def test_connections(self):
        """Test database and API connections"""
        print("\n🔍 STEP 3: TEST CONNECTIONS")
        print("=" * 50)
        
        # Test database connection
        print("\n📊 Testing database connection...")
        try:
            conn_params = {
                'host': f"db.{self.credentials['project_id']}.supabase.co",
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': self.credentials['db_password'],
                'sslmode': 'require'
            }
            
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Database connected: {version[:50]}...")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Test Supabase client
        print("\n🚀 Testing Supabase API...")
        try:
            from supabase import create_client
            supabase = create_client(
                self.credentials['project_url'],
                self.credentials['service_key']
            )
            print("✅ Supabase API connection successful")
        except ImportError:
            print("⚠️  Supabase package not installed - will install later")
        except Exception as e:
            print(f"❌ Supabase API connection failed: {e}")
            return False
        
        return True
    
    def install_dependencies(self):
        """Install required packages"""
        print("\n📦 STEP 4: INSTALL DEPENDENCIES")
        print("=" * 50)
        
        packages = [
            'supabase==2.3.4',
            'django-storages==1.14.2',
            'boto3==1.34.34'
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True, capture_output=True)
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
        
        return True
    
    def migrate_database(self):
        """Migrate existing database to Supabase"""
        print("\n🔄 STEP 5: MIGRATE DATABASE")
        print("=" * 50)
        
        # Check if local database exists
        local_exists = self.check_local_database()
        
        if local_exists:
            print("📊 Found existing local database")
            migrate = input("Do you want to migrate your existing data? (yes/no): ").lower().strip()
            
            if migrate in ['yes', 'y']:
                return self.run_data_migration()
            else:
                print("⏭️  Skipping data migration")
                return self.run_fresh_migration()
        else:
            print("🆕 No existing database found - creating fresh schema")
            return self.run_fresh_migration()
    
    def check_local_database(self):
        """Check if local database exists"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='erabase_db',
                user='erabase_user',
                password='131313'
            )
            conn.close()
            return True
        except:
            return False
    
    def run_data_migration(self):
        """Run full data migration from local to Supabase"""
        print("\n🔄 Migrating existing data...")
        
        try:
            # Import and run the migration
            from migrate_existing_data import DatabaseMigrator
            
            migrator = DatabaseMigrator()
            migrator.target_config['password'] = self.credentials['db_password']
            migrator.target_config['host'] = f"db.{self.credentials['project_id']}.supabase.co"
            
            success = migrator.migrate()
            if success:
                print("✅ Data migration completed successfully")
                return True
            else:
                print("❌ Data migration failed")
                return False
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False
    
    def run_fresh_migration(self):
        """Run Django migrations on fresh database"""
        print("\n🆕 Creating fresh database schema...")
        
        try:
            # Set environment variables
            os.environ['DJANGO_SETTINGS_MODULE'] = 'machine_logbook.settings'
            
            # Run Django migrations
            import django
            django.setup()
            
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'migrate'])
            
            print("✅ Fresh database schema created")
            return True
        except Exception as e:
            print(f"❌ Django migration failed: {e}")
            return False
    
    def setup_storage(self):
        """Set up Supabase storage bucket"""
        print("\n🗄️  STEP 6: SETUP STORAGE")
        print("=" * 50)
        
        try:
            from supabase import create_client
            
            supabase = create_client(
                self.credentials['project_url'],
                self.credentials['service_key']
            )
            
            bucket_name = 'machine-maintenance-media'
            
            # Create bucket
            try:
                supabase.storage.create_bucket(bucket_name, {
                    'public': True,
                    'fileSizeLimit': 52428800  # 50MB
                })
                print(f"✅ Storage bucket '{bucket_name}' created")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Storage bucket '{bucket_name}' already exists")
                else:
                    print(f"❌ Failed to create bucket: {e}")
                    return False
            
            # Test upload
            test_content = b"Test file for Supabase storage"
            test_file = "test/connection_test.txt"
            
            try:
                supabase.storage.from_(bucket_name).upload(test_file, test_content)
                print("✅ Storage upload test successful")
                
                # Clean up test file
                supabase.storage.from_(bucket_name).remove([test_file])
                print("🧹 Test file cleaned up")
            except Exception as e:
                print(f"⚠️  Storage upload test failed: {e}")
            
            return True
        except Exception as e:
            print(f"❌ Storage setup failed: {e}")
            return False
    
    def create_admin_user(self):
        """Guide user to create admin user"""
        print("\n👤 STEP 7: CREATE ADMIN USER")
        print("=" * 50)
        
        print("Now let's create an admin user for your application.")
        print()
        create_user = input("Do you want to create an admin user now? (yes/no): ").lower().strip()
        
        if create_user in ['yes', 'y']:
            try:
                os.environ['DJANGO_SETTINGS_MODULE'] = 'machine_logbook.settings'
                import django
                django.setup()
                
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'createsuperuser'])
                
                print("✅ Admin user created successfully")
            except Exception as e:
                print(f"❌ Failed to create admin user: {e}")
                print("You can create one later with: python manage.py createsuperuser")
        else:
            print("⏭️  You can create an admin user later with: python manage.py createsuperuser")
        
        return True
    
    def final_verification(self):
        """Final verification and testing"""
        print("\n✅ STEP 8: FINAL VERIFICATION")
        print("=" * 50)
        
        try:
            # Test Django app
            print("🧪 Testing Django application...")
            os.environ['DJANGO_SETTINGS_MODULE'] = 'machine_logbook.settings'
            import django
            django.setup()
            
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_migrations;")
                migrations = cursor.fetchone()[0]
                print(f"✅ Django app working - {migrations} migrations applied")
            
            # Check models
            from issues.models import Issue
            issue_count = Issue.objects.count()
            print(f"✅ Models accessible - {issue_count} issues in database")
            
            return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps after successful deployment"""
        print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"\n🌐 Your application is now deployed to Supabase!")
        print(f"🔗 Dashboard: {self.credentials['project_url']}")
        print()
        
        print("📝 NEXT STEPS:")
        print()
        print("1. 🚀 START YOUR DJANGO SERVER:")
        print("   python manage.py runserver")
        print("   Open: http://localhost:8000")
        print()
        
        print("2. 🔧 UPDATE YOUR FRONTEND:")
        print("   Update your React app's environment variables:")
        print(f"   VITE_API_BASE_URL=http://localhost:8000/api")
        print(f"   VITE_SUPABASE_URL={self.credentials['project_url']}")
        print(f"   VITE_SUPABASE_ANON_KEY={self.credentials['anon_key'][:20]}...")
        print()
        
        print("3. 📁 UPLOAD EXISTING MEDIA FILES:")
        print("   Go to Supabase Dashboard → Storage → machine-maintenance-media")
        print("   Upload your existing images and videos")
        print()
        
        print("4. 🧪 TEST YOUR APPLICATION:")
        print("   • Create a test issue")
        print("   • Upload an image or video")
        print("   • Verify everything works correctly")
        print()
        
        print("5. 🚀 DEPLOY TO PRODUCTION (Optional):")
        print("   • Update DEBUG=False in .env")
        print("   • Add your domain to ALLOWED_HOSTS")
        print("   • Deploy your frontend to Vercel/Netlify")
        print("   • Update CORS settings for production")
        print()
        
        print("📊 MONITOR YOUR USAGE:")
        print(f"   Dashboard: {self.credentials['project_url']}/project/default")
        print("   • Database usage and connections")
        print("   • Storage usage and bandwidth")
        print("   • API requests and performance")
        print()
        
        print("🆘 NEED HELP?")
        print("   • Check the SUPABASE_DEPLOYMENT_GUIDE.md file")
        print("   • Run: python test_supabase_setup.py")
        print("   • Visit: https://supabase.com/docs")
    
    def run_setup(self):
        """Run the complete setup process"""
        try:
            self.welcome()
            self.collect_credentials()
            
            if not self.create_env_file():
                return False
            
            if not self.test_connections():
                return False
            
            if not self.install_dependencies():
                return False
            
            if not self.migrate_database():
                return False
            
            if not self.setup_storage():
                return False
            
            self.create_admin_user()
            
            if not self.final_verification():
                return False
            
            self.show_next_steps()
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False


def main():
    """Main setup function"""
    setup = SupabaseSetup()
    success = setup.run_setup()
    
    if not success:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your Supabase credentials are correct")
        print("2. Ensure your Supabase project is active")
        print("3. Verify your internet connection")
        print("4. Run: python test_supabase_setup.py")
        print("\nRun this script again to retry the setup.")
        sys.exit(1)


if __name__ == "__main__":
    main() 