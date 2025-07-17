# Supabase Deployment Guide

This guide will help you deploy your Machine Maintenance Logbook to Supabase, including both database and media storage.

## Prerequisites

1. **Supabase Account**: Create a free account at [supabase.com](https://supabase.com)
2. **Python Environment**: Ensure you have Python 3.8+ and Django environment set up
3. **Local Application**: Your Django application should be working locally

## Step 1: Create Supabase Project

1. Log into your Supabase dashboard
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `machine-maintenance-logbook`
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
5. Wait for project creation (2-3 minutes)

## Step 2: Get Supabase Credentials

From your Supabase project dashboard, collect these values:

### Database Connection
- Go to **Settings → Database**
- Note down:
  - **Host**: `db.xyz.supabase.co`
  - **Database name**: `postgres`
  - **Username**: `postgres`
  - **Password**: The password you set during project creation
  - **Port**: `5432`

### API Keys
- Go to **Settings → API**
- Note down:
  - **Project URL**: `https://xyz.supabase.co`
  - **Anon/Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
  - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### Storage Access Keys
- Go to **Settings → Storage**
- Click "Generate new keys" if none exist
- Note down:
  - **Access Key ID**
  - **Secret Access Key**

## Step 3: Update Environment Variables

Create or update your `.env` file in `project/django_backend/`:

```env
# Database Configuration - Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_db_password
DB_HOST=db.xyz.supabase.co
DB_PORT=5432

# Supabase Configuration
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Supabase Storage Configuration
SUPABASE_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_ACCESS_KEY_ID=your_supabase_access_key
AWS_SECRET_ACCESS_KEY=your_supabase_secret_key
AWS_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_S3_ENDPOINT_URL=https://xyz.supabase.co/storage/v1/s3
AWS_S3_REGION_NAME=us-east-1
AWS_DEFAULT_ACL=public-read

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Media Configuration (will use Supabase Storage)
MEDIA_URL=https://xyz.supabase.co/storage/v1/object/public/machine-maintenance-media/
USE_S3=True
```

**Important**: Replace `xyz` with your actual Supabase project ID in all URLs!

## Step 4: Install Dependencies

```bash
cd project/django_backend
pip install -r requirements.txt
```

## Step 5: Run Deployment Script

Run the automated deployment script:

```bash
python deploy_to_supabase.py
```

This script will:
1. ✅ Check environment configuration
2. 📦 Install Supabase dependencies
3. 🔗 Test database connection
4. 📊 Run Django migrations
5. 🗄️ Setup storage bucket
6. 👤 Check for admin user
7. 📁 Handle existing media files
8. ✅ Verify deployment

## Step 6: Manual Storage Setup

If the storage setup fails, manually create the bucket:

1. Go to **Storage** in your Supabase dashboard
2. Click "Create a new bucket"
3. Name: `machine-maintenance-media`
4. Make it **Public**
5. Set file size limit to **50MB**

### Setup Storage Policies

Go to **Storage → machine-maintenance-media → Configuration → Policies** and create:

1. **Enable read access for all users**
   ```sql
   SELECT: true
   ```

2. **Enable insert for authenticated users**
   ```sql
   INSERT: auth.role() = 'authenticated'
   ```

3. **Enable update for authenticated users**
   ```sql
   UPDATE: auth.role() = 'authenticated'
   ```

4. **Enable delete for authenticated users**
   ```sql
   DELETE: auth.role() = 'authenticated'
   ```

## Step 7: Create Admin User

```bash
python manage.py createsuperuser
```

## Step 8: Test Your Deployment

### Test Database
```bash
python supabase_utils.py
```

### Test Django Admin
1. Run your Django server: `python manage.py runserver`
2. Go to `http://localhost:8000/admin/`
3. Login with your superuser credentials
4. Verify you can see your models and data

### Test File Upload
1. Create a test issue through your frontend
2. Upload an image or video
3. Verify the file appears in Supabase Storage
4. Check that the URL works

## Step 9: Update Frontend Configuration

Update your frontend environment variables:

```env
VITE_API_BASE_URL=https://xyz.supabase.co/rest/v1
VITE_SUPABASE_URL=https://xyz.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

## Production Deployment

### For Production Servers

1. **Set DEBUG=False** in your .env file
2. **Update ALLOWED_HOSTS** with your domain
3. **Add CORS origins** for your production frontend
4. **Use HTTPS** - set secure cookie settings
5. **Monitor usage** - check Supabase dashboard regularly

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
PRODUCTION_DOMAINS=your-domain.com,www.your-domain.com
USE_S3=True
```

## Troubleshooting

### Database Connection Issues
- ✅ Check your database credentials in .env
- ✅ Verify your Supabase project is active
- ✅ Ensure SSL is enabled (automatic with Supabase)
- ✅ Test connection with: `python test_db_connection.py`

### Storage Issues
- ✅ Verify storage access keys are correct
- ✅ Check bucket name matches exactly
- ✅ Ensure bucket is public
- ✅ Test storage with: `python supabase_utils.py`

### Migration Issues
- ✅ Backup your local database first
- ✅ Check Django migrations are applied locally
- ✅ Run migrations step by step if needed

### File Upload Issues
- ✅ Check file size limits (50MB default)
- ✅ Verify CORS policies for storage
- ✅ Ensure media URLs are correctly configured

## Monitoring and Maintenance

### Supabase Dashboard
- **Database**: Monitor connections, queries, and storage usage
- **Storage**: Track file uploads and bandwidth usage
- **Auth**: Manage users and authentication
- **API**: Monitor API usage and performance

### Usage Limits (Free Tier)
- **Database**: 500MB storage
- **Storage**: 1GB files
- **Bandwidth**: 2GB transfer
- **API Requests**: 50,000 per month

### Backup Strategy
- **Database**: Use `pg_dump` for regular backups
- **Storage**: Download important files periodically
- **Settings**: Keep environment variables backed up

## Support

If you encounter issues:

1. Check the Supabase [documentation](https://supabase.com/docs)
2. Review Django-storages [documentation](https://django-storages.readthedocs.io/)
3. Check Supabase [community forum](https://github.com/supabase/supabase/discussions)
4. Review error logs in your Django application

## Next Steps

After successful deployment:

1. 🎯 Set up monitoring and alerts
2. 📊 Configure analytics and logging
3. 🔒 Review security settings
4. 🚀 Deploy your frontend to a hosting service
5. 📝 Document your production URLs and processes

---

*Your Machine Maintenance Logbook is now running on Supabase! 🎉* 