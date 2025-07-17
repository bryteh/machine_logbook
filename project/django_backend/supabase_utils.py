#!/usr/bin/env python
"""
Supabase utilities for machine maintenance logbook
"""
import os
import django
from supabase import create_client, Client
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

class SupabaseManager:
    def __init__(self):
        self.url = config('SUPABASE_URL')
        self.key = config('SUPABASE_SERVICE_ROLE_KEY')
        self.anon_key = config('SUPABASE_ANON_KEY')
        
        if not all([self.url, self.key]):
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
            
        self.supabase: Client = create_client(self.url, self.key)
    
    def test_connection(self):
        """Test Supabase connection"""
        try:
            # Test with a simple query
            result = self.supabase.table('auth.users').select('*').limit(1).execute()
            print(f"✅ Supabase connection successful!")
            print(f"🔗 URL: {self.url}")
            return True
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False
    
    def create_storage_bucket(self, bucket_name='machine-maintenance-media'):
        """Create storage bucket for media files"""
        try:
            # Create bucket
            result = self.supabase.storage.create_bucket(bucket_name, {
                'public': True,
                'allowedMimeTypes': [
                    'image/*',
                    'video/*',
                    'application/pdf',
                    'text/*'
                ],
                'fileSizeLimit': 52428800  # 50MB
            })
            print(f"✅ Storage bucket '{bucket_name}' created successfully!")
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Storage bucket '{bucket_name}' already exists")
                return True
            else:
                print(f"❌ Failed to create storage bucket: {e}")
                return False
    
    def setup_storage_policies(self, bucket_name='machine-maintenance-media'):
        """Setup RLS policies for storage bucket"""
        policies = [
            {
                'name': 'Enable read access for all users',
                'command': 'SELECT',
                'definition': 'true'
            },
            {
                'name': 'Enable insert for authenticated users only',
                'command': 'INSERT', 
                'definition': 'auth.role() = \'authenticated\''
            },
            {
                'name': 'Enable update for authenticated users only',
                'command': 'UPDATE',
                'definition': 'auth.role() = \'authenticated\''
            },
            {
                'name': 'Enable delete for authenticated users only',
                'command': 'DELETE',
                'definition': 'auth.role() = \'authenticated\''
            }
        ]
        
        print(f"📋 Setting up storage policies for '{bucket_name}'...")
        print("⚠️  Note: You may need to manually create these policies in the Supabase dashboard:")
        print(f"   Storage → {bucket_name} → Configuration → Policies")
        
        for policy in policies:
            print(f"   - {policy['name']}: {policy['definition']}")
        
        return True
    
    def test_storage_upload(self, bucket_name='machine-maintenance-media'):
        """Test storage upload with a small test file"""
        try:
            test_content = b"Test file content for Supabase storage"
            test_filename = "test/connection_test.txt"
            
            # Upload test file
            result = self.supabase.storage.from_(bucket_name).upload(
                test_filename, 
                test_content,
                {'content-type': 'text/plain'}
            )
            
            print(f"✅ Test file uploaded successfully!")
            
            # Get public URL
            public_url = self.supabase.storage.from_(bucket_name).get_public_url(test_filename)
            print(f"🔗 Public URL: {public_url}")
            
            # Clean up test file
            self.supabase.storage.from_(bucket_name).remove([test_filename])
            print(f"🧹 Test file cleaned up")
            
            return True
        except Exception as e:
            print(f"❌ Storage upload test failed: {e}")
            return False
    
    def check_database_tables(self):
        """Check if Django tables exist in Supabase"""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'issues_%' OR table_name LIKE 'django_%'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                print(f"📊 Found {len(tables)} Django/app tables:")
                for table in tables:
                    print(f"   - {table[0]}")
                
                return len(tables) > 0
        except Exception as e:
            print(f"❌ Database table check failed: {e}")
            return False
    
    def get_bucket_info(self, bucket_name='machine-maintenance-media'):
        """Get information about the storage bucket"""
        try:
            # List files in bucket
            result = self.supabase.storage.from_(bucket_name).list()
            print(f"📁 Bucket '{bucket_name}' contains {len(result)} items:")
            
            for item in result[:10]:  # Show first 10 items
                print(f"   - {item['name']} ({item.get('metadata', {}).get('size', 'Unknown size')})")
            
            if len(result) > 10:
                print(f"   ... and {len(result) - 10} more items")
                
            return True
        except Exception as e:
            print(f"❌ Failed to get bucket info: {e}")
            return False


def main():
    """Main function to test and setup Supabase"""
    print("🚀 Supabase Setup and Testing")
    print("=" * 50)
    
    try:
        manager = SupabaseManager()
        
        # Test connection
        print("\n1. Testing Supabase connection...")
        if not manager.test_connection():
            return
        
        # Create storage bucket
        print("\n2. Setting up storage bucket...")
        bucket_name = config('SUPABASE_STORAGE_BUCKET_NAME', default='machine-maintenance-media')
        manager.create_storage_bucket(bucket_name)
        
        # Setup policies (informational)
        print("\n3. Storage policies setup...")
        manager.setup_storage_policies(bucket_name)
        
        # Test storage upload
        print("\n4. Testing storage upload...")
        manager.test_storage_upload(bucket_name)
        
        # Check database tables
        print("\n5. Checking database tables...")
        manager.check_database_tables()
        
        # Get bucket info
        print("\n6. Getting bucket information...")
        manager.get_bucket_info(bucket_name)
        
        print("\n✅ Supabase setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Run 'python manage.py migrate' to create Django tables")
        print("   2. Run 'python manage.py createsuperuser' to create admin user") 
        print("   3. Update your frontend to use the new Supabase URLs")
        print("   4. Test file uploads through your application")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file has all required Supabase variables")
        print("   2. Verify your Supabase project is active")
        print("   3. Ensure your service role key has admin permissions")


if __name__ == "__main__":
    main() 