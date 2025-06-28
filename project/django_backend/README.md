# Erabase Machine Issue Logbook - Django Backend

A Django REST API backend for tracking machine issues, downtime, and remedies in a CNC machining factory.

## Features

- **Machine Issue Tracking**: Log and track machine problems with categories, alarm codes, and descriptions
- **AI Integration**: GPT-4o-mini powered summaries and auto-titles for issues
- **OCR Support**: Extract alarm codes from uploaded images using Tesseract
- **File Attachments**: Support for photos and videos with validation
- **Dashboard Metrics**: Real-time statistics and trend analysis
- **Database Integration**: Connects to existing `erabase_db` PostgreSQL database

## Technology Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (connects to existing `erabase_db`)
- **AI**: OpenAI GPT-4o-mini
- **OCR**: Tesseract.js/pytesseract
- **File Storage**: Local filesystem (extensible to S3)

## Quick Setup

### 1. Environment Setup

```bash
# Navigate to backend directory
cd django_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Create a `.env` file in the `django_backend` directory (copy from `env_example.txt`):

```env
# Database Configuration
DB_NAME=erabase_db
DB_USER=your_postgresql_username
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Media Configuration
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

### 3. Database Migration

The system connects to existing `manufacturing_machine` and `manufacturing_department` tables:

```bash
# Create Django migrations for new models only
python manage.py makemigrations

# Apply migrations (only for Issue, Remedy, Attachment tables)
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver 8000
```

The API will be available at: `http://localhost:8000/api/`

## API Endpoints

### Core Resources

- `GET /api/machines/` - List all manufacturing machines
- `GET /api/departments/` - List all manufacturing departments
- `GET /api/issues/` - List issues (with filtering)
- `POST /api/issues/` - Create new issue
- `GET /api/issues/{id}/` - Get issue details
- `PATCH /api/issues/{id}/update_status/` - Update issue status
- `POST /api/issues/{id}/add_remedy/` - Add remedy to issue

### Dashboard

- `GET /api/dashboard/metrics/?days=30` - Get dashboard statistics

### Filtering Examples

```bash
# Filter issues by status
GET /api/issues/?status=open

# Filter by machine
GET /api/issues/?machine=machine-uuid

# Search by description or title
GET /api/issues/?search=pump

# Combine filters
GET /api/issues/?status=open&category=alarm&is_runnable=true
```

## Database Schema

### Existing Tables (Read-Only)
- `manufacturing_machine` - Machine definitions
- `manufacturing_department` - Department definitions

### New Tables (Managed by Django)
- `issues_issue` - Machine issues
- `issues_remedy` - Remedies/solutions
- `issues_attachment` - File attachments

## AI Features

### OpenAI Integration
When creating issues, the system automatically:
1. Generates cleaned summaries of issue descriptions
2. Creates concise, descriptive titles
3. Improves remedy descriptions

### OCR Integration
- Automatically extracts alarm codes from uploaded images
- Supports common alarm patterns (ALARM: 123, ERROR: 456, etc.)
- Updates issue records with extracted text

## File Upload

### Supported Formats
- **Images**: JPG, JPEG, PNG, GIF
- **Videos**: MP4, MOV, AVI
- **Size Limit**: 10MB per file

### File Organization
```
media/
  attachments/
    2024/
      01/
        15/
          alarm-screen-image.jpg
          repair-video.mp4
```

## Development

### Project Structure
```
django_backend/
├── machine_logbook/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── issues/                   # Main application
│   ├── models.py            # Database models
│   ├── serializers.py       # API serializers
│   ├── views.py             # API views
│   ├── services.py          # AI/OCR services
│   ├── admin.py             # Django admin
│   └── urls.py              # URL routing
├── media/                   # File uploads
├── requirements.txt         # Python dependencies
└── manage.py               # Django management
```

### Running Tests
```bash
python manage.py test
```

### Admin Interface
Access Django admin at: `http://localhost:8000/admin/`

## Production Deployment

### Environment Variables
Set these in your production environment:
- `DEBUG=False`
- `SECRET_KEY=production-secret-key`
- `ALLOWED_HOSTS=yourdomain.com`
- `DB_PASSWORD=secure-password`

### Static Files
```bash
python manage.py collectstatic
```

### WSGI/ASGI
Use `machine_logbook.wsgi` or `machine_logbook.asgi` for deployment.

## Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL is running
2. Verify connection settings in `.env`
3. Check that `erabase_db` database exists
4. Ensure `manufacturing_machine` and `manufacturing_department` tables exist

### AI Features Not Working
1. Check `OPENAI_API_KEY` in `.env`
2. Verify OpenAI API quota and permissions
3. Issues will still be created without AI processing

### OCR Issues
1. Install Tesseract system dependency
2. Check image file formats are supported
3. Ensure sufficient image quality

## Support

For issues related to:
- Database connectivity: Check PostgreSQL configuration
- AI features: Verify OpenAI API key and quota
- File uploads: Check media directory permissions
- General setup: Review environment variables in `.env` 