# Erabase Machine Logbook - Deployment Guide

This guide will help you deploy the complete Machine Issue Logbook system using Django backend and React frontend.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │───▶│ Django REST API │───▶│ PostgreSQL DB   │
│   (Port 5173)   │    │   (Port 8000)   │    │ (erabase_db)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 12+** (with existing `erabase_db` database)
- **Git** for version control

## Part 1: Database Setup

### 1.1 PostgreSQL Configuration

Ensure you have a PostgreSQL database named `erabase_db`:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database if it doesn't exist
CREATE DATABASE erabase_db;

-- Create user (optional)
CREATE USER logbook_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE erabase_db TO logbook_user;
```

### 1.2 Verify Existing Tables

The system connects to existing `manufacturing_machine` and `manufacturing_department` tables. If they don't exist, our setup script will create them.

## Part 2: Django Backend Setup

### 2.1 Environment Setup

```bash
# Navigate to backend directory
cd project/django_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Environment Configuration

Create `.env` file in `django_backend/` directory:

```env
# Database Configuration
DB_NAME=erabase_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Media Configuration
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

### 2.3 Database Initialization

```bash
# Run the database setup script
python setup_database.py

# Create Django migrations
python manage.py makemigrations

# Apply migrations (creates Issue, Remedy, Attachment tables)
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 2.4 Test Backend

```bash
# Start Django development server
python manage.py runserver 8000

# Test API endpoints
curl http://localhost:8000/api/machines/
curl http://localhost:8000/api/departments/
curl http://localhost:8000/api/dashboard/metrics/
```

## Part 3: React Frontend Setup

### 3.1 Install Dependencies

```bash
# Navigate to project root
cd ../

# Install Node.js dependencies
npm install
```

### 3.2 Environment Configuration

The frontend is already configured to connect to Django backend at `http://localhost:8000/api`.

### 3.3 Start Frontend

```bash
# Start Vite development server
npm run dev

# Frontend will be available at http://localhost:5173
```

## Part 4: Full System Test

### 4.1 Start Both Services

```bash
# Terminal 1: Start Django backend
cd project/django_backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver 8000

# Terminal 2: Start React frontend
cd project
npm run dev
```

### 4.2 Test Core Features

1. **Dashboard**: Visit `http://localhost:5173` - should show metrics
2. **Machine List**: Check that machines and departments load
3. **Create Issue**: Test the "Log New Issue" functionality
4. **File Upload**: Test image/video upload (if configured)
5. **AI Features**: Test if OpenAI integration works (if API key provided)

## Part 5: Production Deployment

### 5.1 Backend Production Settings

Update `.env` for production:

```env
DEBUG=False
SECRET_KEY=very-secure-production-key
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DB_PASSWORD=secure-production-password
```

### 5.2 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 5.3 WSGI Deployment

Use `machine_logbook.wsgi` with:
- **Gunicorn**: `gunicorn machine_logbook.wsgi:application`
- **uWSGI**: Configure with `machine_logbook.wsgi`
- **Apache**: Use mod_wsgi

### 5.4 Frontend Production Build

```bash
# Build optimized production frontend
npm run build

# Serve with nginx, Apache, or CDN
# Built files will be in project/dist/
```

### 5.5 Nginx Configuration Example

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /media/ {
        alias /path/to/django_backend/media/;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/project/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Part 6: Optional Features Setup

### 6.1 OpenAI Integration

1. Get API key from [OpenAI](https://platform.openai.com/)
2. Add to `.env`: `OPENAI_API_KEY=sk-your-key`
3. Restart Django server

### 6.2 OCR Setup (Tesseract)

```bash
# Install Tesseract
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: Download from GitHub releases
```

### 6.3 File Storage (S3)

For production file storage, update Django settings:

```python
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
```

## Part 7: Troubleshooting

### 7.1 Common Issues

**Database Connection Failed:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d erabase_db -c "SELECT 1;"
```

**API Not Loading:**
- Verify Django server is running on port 8000
- Check CORS settings in Django
- Ensure frontend API URL is correct

**File Upload Issues:**
- Check media directory permissions
- Verify file size limits
- Test with smaller files first

**AI Features Not Working:**
- Verify OpenAI API key
- Check API quota/billing
- Look for errors in Django logs

### 7.2 Log Files

Check these locations for debugging:
- Django: `python manage.py runserver` output
- Frontend: Browser console (F12)
- PostgreSQL: `/var/log/postgresql/`

## Part 8: Maintenance

### 8.1 Database Backups

```bash
# Backup
pg_dump -U postgres erabase_db > backup.sql

# Restore
psql -U postgres erabase_db < backup.sql
```

### 8.2 Updates

```bash
# Update backend dependencies
pip install -r requirements.txt --upgrade

# Update frontend dependencies
npm update

# Apply new migrations
python manage.py migrate
```

### 8.3 Monitoring

Monitor these metrics:
- API response times
- Database connection pool
- File storage usage
- OpenAI API usage/costs

## Support

- **Backend Issues**: Check Django logs and database connectivity
- **Frontend Issues**: Check browser console and network requests
- **Database Issues**: Verify PostgreSQL service and permissions
- **AI Issues**: Confirm OpenAI API key and quota

The system is now ready for production use! 🎉 