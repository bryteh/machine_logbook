#!/usr/bin/env python
"""
Simple script to check Django configuration and database
"""
import os
import sys
import django

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')

print("🔍 Checking Django Configuration")
print("=" * 50)

try:
    # Setup Django
    django.setup()
    print("✅ Django setup successful")
    
    # Check database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
    
    # Check if migrations are needed
    from django.core.management import execute_from_command_line
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    f = io.StringIO()
    try:
        with redirect_stdout(f), redirect_stderr(f):
            execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
        migration_output = f.getvalue()
        if "[ ]" in migration_output:
            print("⚠️  Unapplied migrations found")
        else:
            print("✅ All migrations applied")
    except Exception as e:
        print(f"⚠️  Migration check error: {e}")
    
    # Check models
    from issues.models import Issue, Remedy, UserRole
    print(f"✅ Models accessible - Issues: {Issue.objects.count()}")
    
    print("\n🚀 Django is ready to run!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()