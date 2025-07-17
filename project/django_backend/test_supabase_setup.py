#!/usr/bin/env python
"""
Quick test script to validate Supabase setup
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from django.db import connection
from django.conf import settings
from decouple import config

def test_database_connection():
    """Test PostgreSQL connection to Supabase"""
    print("🔍 Testing Database Connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Database connected: {version[:50]}...")
            
            # Test a simple query
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(f"📊 Database: {db_info[0]}, User: {db_info[1]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_storage_configuration():
    """Test storage configuration"""
    print("\n🗄️  Testing Storage Configuration...")
    
    use_s3 = getattr(settings, 'USE_S3', False)
    if not use_s3:
        print("⚠️  USE_S3 is False - using local storage")
        return True
    
    required_settings = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_ENDPOINT_URL'
    ]
    
    missing = []
    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            missing.append(setting)
    
    if missing:
        print(f"❌ Missing storage settings: {', '.join(missing)}")
        return False
    
    print("✅ Storage configuration looks good")
    print(f"📁 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"🔗 Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
    return True

def test_supabase_client():
    """Test Supabase Python client"""
    print("\n🚀 Testing Supabase Client...")
    
    try:
        from supabase import create_client
        
        url = config('SUPABASE_URL', default='')
        key = config('SUPABASE_SERVICE_ROLE_KEY', default='')
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
            return False
        
        supabase = create_client(url, key)
        print(f"✅ Supabase client created")
        print(f"🔗 URL: {url}")
        return True
    except ImportError:
        print("❌ Supabase package not installed. Run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Supabase client error: {e}")
        return False

def test_environment_variables():
    """Check all required environment variables"""
    print("\n📋 Checking Environment Variables...")
    
    required_vars = {
        'SUPABASE_URL': config('SUPABASE_URL', default=''),
        'SUPABASE_SERVICE_ROLE_KEY': config('SUPABASE_SERVICE_ROLE_KEY', default=''),
        'DB_HOST': config('DB_HOST', default=''),
        'DB_PASSWORD': config('DB_PASSWORD', default=''),
        'USE_S3': config('USE_S3', default='False'),
    }
    
    optional_vars = {
        'AWS_ACCESS_KEY_ID': config('AWS_ACCESS_KEY_ID', default=''),
        'AWS_SECRET_ACCESS_KEY': config('AWS_SECRET_ACCESS_KEY', default=''),
        'SUPABASE_ANON_KEY': config('SUPABASE_ANON_KEY', default=''),
    }
    
    # Check required variables
    missing_required = []
    for var, value in required_vars.items():
        if not value:
            missing_required.append(var)
        else:
            if var == 'SUPABASE_SERVICE_ROLE_KEY':
                print(f"✅ {var}: {value[:20]}...")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    # Check optional variables
    missing_optional = []
    for var, value in optional_vars.items():
        if not value:
            missing_optional.append(var)
        else:
            if 'KEY' in var:
                print(f"✅ {var}: {value[:20]}...")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_optional:
        print(f"\n⚠️  Optional variables not set: {', '.join(missing_optional)}")
        if config('USE_S3', default=False, cast=bool):
            print("   Note: These are required for S3 storage")
    
    return True

def test_django_models():
    """Test Django models can be imported and queried"""
    print("\n📊 Testing Django Models...")
    
    try:
        from issues.models import Issue, ManufacturingMachine, Attachment
        
        # Test basic queries
        issue_count = Issue.objects.count()
        machine_count = ManufacturingMachine.objects.count()
        attachment_count = Attachment.objects.count()
        
        print(f"✅ Models imported successfully")
        print(f"📈 Issues: {issue_count}")
        print(f"🏭 Machines: {machine_count}")
        print(f"📎 Attachments: {attachment_count}")
        return True
    except Exception as e:
        print(f"❌ Model query failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Supabase Setup Validation")
    print("=" * 40)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Database Connection", test_database_connection),
        ("Storage Configuration", test_storage_configuration),
        ("Supabase Client", test_supabase_client),
        ("Django Models", test_django_models),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Supabase setup looks good.")
        print("\n📝 Next steps:")
        print("   1. Run 'python deploy_to_supabase.py' for full deployment")
        print("   2. Test file uploads through your application")
        print("   3. Verify everything works in production")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Update your .env file with correct Supabase credentials")
        print("   2. Ensure your Supabase project is active")
        print("   3. Run 'pip install -r requirements.txt' to install dependencies")
        print("   4. Check the SUPABASE_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main() 