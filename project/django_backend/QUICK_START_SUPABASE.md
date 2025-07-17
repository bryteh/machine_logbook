# 🚀 Quick Start: Deploy to Supabase

## One-Command Setup

```bash
cd project/django_backend
python setup_supabase.py
```

That's it! This script will guide you through everything.

---

## What You Need Before Starting

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login → "New Project"
3. Name: `machine-maintenance-logbook`
4. Choose a strong database password
5. Wait 2-3 minutes for creation

### 2. Collect These Values
**From Supabase Dashboard:**

📍 **Settings → API:**
- Project URL: `https://xyz.supabase.co`
- Anon/Public Key
- Service Role Key

📍 **Settings → Database:**
- Database Password (the one you created)

📍 **Settings → Storage:**
- Access Key ID (click "Generate" if none exist)
- Secret Access Key

---

## Step-by-Step Process

The `setup_supabase.py` script will:

1. ✅ **Collect Credentials** - Guide you through copying from Supabase dashboard
2. ✅ **Create Environment** - Generate your `.env` file automatically
3. ✅ **Test Connections** - Verify everything works
4. ✅ **Install Dependencies** - Add Supabase packages
5. ✅ **Migrate Database** - Move your existing data OR create fresh schema
6. ✅ **Setup Storage** - Create bucket for images/videos
7. ✅ **Create Admin User** - Set up your admin account
8. ✅ **Verify Deployment** - Test everything works

**Total Time:** 10-15 minutes

---

## After Deployment

### Start Your App
```bash
python manage.py runserver
```
Open: http://localhost:8000

### Update Frontend
In your React app, update environment variables:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### Upload Media Files
- Go to Supabase Dashboard → Storage
- Upload your existing images/videos to `machine-maintenance-media` bucket

---

## Manual Steps (If Script Fails)

### 1. Create .env File
```env
# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_HOST=db.your-project-id.supabase.co
DB_PORT=5432

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Storage
AWS_ACCESS_KEY_ID=your_storage_access_key
AWS_SECRET_ACCESS_KEY=your_storage_secret_key
AWS_STORAGE_BUCKET_NAME=machine-maintenance-media
AWS_S3_ENDPOINT_URL=https://your-project-id.supabase.co/storage/v1/s3

# Django
USE_S3=True
DEBUG=True
```

### 2. Install Dependencies
```bash
pip install supabase==2.3.4 django-storages==1.14.2 boto3==1.34.34
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Admin User
```bash
python manage.py createsuperuser
```

---

## Troubleshooting

### Connection Issues
```bash
python test_supabase_setup.py
```

### Database Issues
- Check password in .env file
- Verify project is active in Supabase dashboard
- Ensure SSL is enabled (automatic)

### Storage Issues
- Verify storage keys in .env
- Check bucket exists in Supabase dashboard
- Ensure bucket is public

---

## Need Help?

1. **Test Connection:** `python test_supabase_setup.py`
2. **Check Logs:** Look for error messages in terminal
3. **Documentation:** [Supabase Docs](https://supabase.com/docs)
4. **Re-run Setup:** `python setup_supabase.py`

---

*Your Machine Maintenance Logbook will be running on Supabase in minutes! 🎉* 