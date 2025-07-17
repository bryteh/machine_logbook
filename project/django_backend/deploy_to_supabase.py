#!/usr/bin/env python
"""
Deploy machine maintenance logbook to Supabase
"""
import os
import django
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from decouple import config
import subprocess

class SupabaseDeployer:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        
    def check_environment(self):
        """Check if all required environment variables are set"""
        print("🔍 Checking environment configuration...")
        
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_SERVICE_ROLE_KEY', 
            'DB_HOST',
            'DB_PASSWORD',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_S3_ENDPOINT_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not config(var, default=''):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("📝 Please update your .env file with Supabase credentials")
            return False
        
        print("✅ Environment configuration looks good!")
        return True
    
    def install_dependencies(self):
        """Install required Python packages"""
        print("\n📦 Installing Supabase dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "supabase==2.3.4", 
                "django-storages==1.14.2", 
                "boto3==1.34.34"
            ], check=True, capture_output=True)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def test_database_connection(self):
        """Test connection to Supabase database"""
        print("\n🔗 Testing Supabase database connection...")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"✅ Connected to PostgreSQL: {version}")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Verify DB_HOST, DB_PASSWORD are correct in .env")
            print("   2. Check if your Supabase project is active")
            print("   3. Ensure database has proper SSL configuration")
            return False
    
    def run_migrations(self):
        """Run Django migrations on Supabase database"""
        print("\n📊 Running Django migrations...")
        
        try:
            # First, check if migrations are needed
            execute_from_command_line(['manage.py', 'showmigrations'])
            
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Migrations completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def create_superuser_if_needed(self):
        """Create superuser if none exists"""
        print("\n👤 Checking for admin user...")
        
        try:
            from django.contrib.auth.models import User
            
            if User.objects.filter(is_superuser=True).exists():
                print("✅ Admin user already exists")
                return True
            
            print("📝 No admin user found. You can create one manually with:")
            print("   python manage.py createsuperuser")
            return True
        except Exception as e:
            print(f"❌ Error checking users: {e}")
            return False
    
    def setup_storage(self):
        """Setup Supabase storage"""
        print("\n🗄️  Setting up Supabase storage...")
        
        try:
            from supabase_utils import SupabaseManager
            manager = SupabaseManager()
            
            bucket_name = config('SUPABASE_STORAGE_BUCKET_NAME', default='machine-maintenance-media')
            
            # Create bucket
            manager.create_storage_bucket(bucket_name)
            
            # Test upload
            manager.test_storage_upload(bucket_name)
            
            print("✅ Storage setup completed!")
            return True
        except Exception as e:
            print(f"❌ Storage setup failed: {e}")
            return False
    
    def migrate_existing_media(self):
        """Migrate existing media files to Supabase storage"""
        print("\n📁 Checking for existing media files...")
        
        media_dir = self.project_dir / 'media'
        if not media_dir.exists():
            print("ℹ️  No existing media directory found")
            return True
        
        print(f"📂 Found media directory: {media_dir}")
        print("⚠️  Manual migration required for existing files:")
        print("   1. Use the Supabase dashboard to upload existing files")
        print("   2. Or use the storage API to programmatically migrate")
        print("   3. Update database records with new URLs if needed")
        
        return True
    
    def verify_deployment(self):
        """Verify the deployment is working"""
        print("\n✅ Verifying deployment...")
        
        try:
            # Test database
            from issues.models import Issue, GlobalSettings
            
            # Check if we can query the database
            issue_count = Issue.objects.count()
            print(f"📊 Database working - {issue_count} issues found")
            
            # Test storage configuration
            use_s3 = config('USE_S3', default=False, cast=bool)
            if use_s3:
                print("🗄️  Storage configured for Supabase")
            else:
                print("⚠️  Storage still using local files (set USE_S3=True in .env)")
            
            print("✅ Deployment verification completed!")
            return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def deploy(self):
        """Run the complete deployment process"""
        print("🚀 Starting Supabase Deployment")
        print("=" * 50)
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Install Dependencies", self.install_dependencies),
            ("Database Connection", self.test_database_connection),
            ("Run Migrations", self.run_migrations),
            ("Setup Storage", self.setup_storage),
            ("Check Admin User", self.create_superuser_if_needed),
            ("Migrate Media Files", self.migrate_existing_media),
            ("Verify Deployment", self.verify_deployment),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                print(f"\n❌ Deployment failed at step: {step_name}")
                return False
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n📝 Next Steps:")
        print("1. Update your frontend environment variables:")
        print(f"   - API_BASE_URL={config('SUPABASE_URL', '')}/rest/v1")
        print(f"   - SUPABASE_URL={config('SUPABASE_URL', '')}")
        print(f"   - SUPABASE_ANON_KEY={config('SUPABASE_ANON_KEY', '')}")
        
        print("\n2. Update CORS settings if deploying to production:")
        print("   - Add your production domain to ALLOWED_HOSTS")
        print("   - Update CORS_ALLOWED_ORIGINS in settings.py")
        
        print("\n3. Test your application:")
        print("   - Create a test issue with file upload")
        print("   - Verify files are stored in Supabase Storage")
        print("   - Check that all features work correctly")
        
        print("\n4. Monitor your deployment:")
        print("   - Check Supabase dashboard for usage")
        print("   - Monitor storage and database limits")
        print("   - Set up alerts for errors")
        
        return True


def main():
    """Main deployment function"""
    deployer = SupabaseDeployer()
    success = deployer.deploy()
    
    if not success:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Check your .env file has all Supabase credentials")
        print("2. Verify your Supabase project is active and accessible")
        print("3. Ensure your local environment has internet connectivity")
        print("4. Check the Supabase dashboard for any service issues")
        print("5. Review the error messages above for specific issues")
        sys.exit(1)
    
    print(f"\n🌐 Your application is now deployed to Supabase!")
    print(f"🔗 Dashboard: {config('SUPABASE_URL', '')}")


if __name__ == "__main__":
    main() 