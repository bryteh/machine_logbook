#!/usr/bin/env python
"""
Helper script to get Supabase credentials and create .env file
"""

def get_supabase_credentials():
    """Guide user through getting Supabase credentials"""
    
    print("🔑 Supabase Credentials Setup")
    print("=" * 40)
    print()
    print("We already have your database connection details.")
    print("Now we need a few more credentials from your Supabase dashboard.")
    print()
    
    # Known values
    project_id = "spqxhiavpnajramwjacs"
    db_password = "23,JalanIstimewa4"
    
    print(f"✅ Project ID: {project_id}")
    print(f"✅ Database Password: {db_password}")
    print()
    
    print("📋 Please get these values from your Supabase dashboard:")
    print()
    
    # Step 1: API Keys
    print("1️⃣  API KEYS")
    print("   Go to: Settings → API")
    print("   Copy these two keys:")
    print()
    anon_key = input("   📝 Paste your ANON/PUBLIC KEY here: ").strip()
    service_key = input("   📝 Paste your SERVICE ROLE KEY here: ").strip()
    
    print()
    
    # Step 2: Storage Keys  
    print("2️⃣  STORAGE KEYS")
    print("   Go to: Settings → Storage")
    print("   If no keys exist, click 'Generate new keys'")
    print()
    access_key = input("   📝 Paste your ACCESS KEY ID here: ").strip()
    secret_key = input("   📝 Paste your SECRET ACCESS KEY here: ").strip()
    
    print()
    
    # Step 3: Optional settings
    print("3️⃣  OPTIONAL SETTINGS")
    print()
    openai_key = input("   📝 OpenAI API Key (optional, press Enter to skip): ").strip()
    secret_key_django = input("   📝 Django Secret Key (press Enter for default): ").strip()
    
    if not secret_key_django:
        secret_key_django = "your-secret-key-change-this-in-production"
    
    # Generate .env content
    env_content = f"""# Database Configuration - Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD={db_password}
DB_HOST=db.{project_id}.supabase.co
DB_PORT=5432

# Supabase Configuration
SUPABASE_URL=https://{project_id}.supabase.co
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# Supabase Storage Configuration
SUPABASE_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_ACCESS_KEY_ID={access_key}
AWS_SECRET_ACCESS_KEY={secret_key}
AWS_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_S3_ENDPOINT_URL=https://{project_id}.supabase.co/storage/v1/s3
AWS_S3_REGION_NAME=us-east-1
AWS_DEFAULT_ACL=public-read

# Django Configuration
SECRET_KEY={secret_key_django}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# Media Configuration (will use Supabase Storage)
MEDIA_URL=https://{project_id}.supabase.co/storage/v1/object/public/machine-maintenance-media/
USE_S3=True
"""
    
    # Save to file
    print("\n💾 Creating .env file...")
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
    except Exception as e:
        print(f"❌ Could not create .env file: {e}")
        print("\n📝 Please create .env file manually with this content:")
        print(env_content)
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Install dependencies: pip install -r requirements.txt")
    print("2. ✅ Test connection: python test_supabase_setup.py")
    print("3. ✅ Migrate your data: python migrate_existing_data.py")
    print("4. ✅ Set up storage: python supabase_utils.py")
    
    return True


def show_dashboard_instructions():
    """Show detailed instructions for finding credentials in Supabase dashboard"""
    
    print("\n📖 Detailed Instructions")
    print("=" * 40)
    
    print("\n🔗 Go to: https://supabase.com/dashboard/projects")
    print("   → Click on your 'machine-maintenance-logbook' project")
    print()
    
    print("📍 Getting API Keys:")
    print("   1. Click 'Settings' in the left sidebar")
    print("   2. Click 'API' in the settings menu")
    print("   3. You'll see two keys:")
    print("      • 'anon public' key - copy this for SUPABASE_ANON_KEY")
    print("      • 'service_role' key - copy this for SUPABASE_SERVICE_ROLE_KEY")
    print()
    
    print("📍 Getting Storage Keys:")
    print("   1. Click 'Settings' in the left sidebar")
    print("   2. Click 'Storage' in the settings menu")
    print("   3. If you see 'No access keys', click 'Generate new keys'")
    print("   4. Copy both keys:")
    print("      • 'Access Key ID' - copy this for AWS_ACCESS_KEY_ID")
    print("      • 'Secret Access Key' - copy this for AWS_SECRET_ACCESS_KEY")
    print()
    
    print("⚠️  Important Notes:")
    print("   • Keep these keys secure - don't share them publicly")
    print("   • The service role key has admin access to your database")
    print("   • Storage keys allow file uploads to your Supabase Storage")
    print()


def main():
    """Main function"""
    print("🚀 Supabase Credentials Helper")
    print()
    print("This script will help you:")
    print("✅ Get your Supabase API keys")
    print("✅ Get your Supabase Storage keys") 
    print("✅ Create a complete .env file")
    print()
    
    choice = input("Do you want to see detailed instructions first? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        show_dashboard_instructions()
        input("\nPress Enter when you're ready to enter your credentials...")
    
    get_supabase_credentials()
    
    print("\n🎉 Setup complete! Your .env file is ready.")
    print("You can now run your migration and deployment scripts.")


if __name__ == "__main__":
    main() 