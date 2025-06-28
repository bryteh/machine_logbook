# Reset PostgreSQL Password Guide

Since you can't remember your PostgreSQL password, here are the steps to reset it:

## Method 1: Reset via Windows Services

1. **Open Services** (Run → `services.msc`)
2. **Find and stop** `postgresql-x64-17` service
3. **Navigate to PostgreSQL data directory** (usually `C:\Program Files\PostgreSQL\17\data\`)
4. **Edit `pg_hba.conf`** file:
   - Find the line that starts with: `host    all             all             127.0.0.1/32            md5`
   - Change `md5` to `trust`
   - Save the file
5. **Restart PostgreSQL service**
6. **Open Command Prompt as Administrator** and run:
   ```
   psql -U postgres -h localhost
   ALTER USER postgres PASSWORD 'your_new_password';
   \q
   ```
7. **Change `pg_hba.conf` back** from `trust` to `md5`
8. **Restart PostgreSQL service** again

## Method 2: Using pgAdmin (if installed)

1. Open pgAdmin
2. Right-click on the PostgreSQL server
3. Select "Properties" → "Definition" tab
4. Change the password

## Method 3: Reinstall PostgreSQL (if other methods don't work)

If the above doesn't work, you can reinstall PostgreSQL and set a new password during installation.

## After Resetting Password

1. Update the `.env` file with your new password:
   ```
   DB_PASSWORD=your_new_password_here
   ```

2. Update `settings.py` to use PostgreSQL:
   ```python
   # Uncomment the PostgreSQL config and comment out SQLite
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME', default='erabase_db'),
           'USER': config('DB_USER', default='postgres'),
           'PASSWORD': config('DB_PASSWORD', default=''),
           'HOST': config('DB_HOST', default='localhost'),
           'PORT': config('DB_PORT', default='5432'),
       }
   }
   ```

3. Test the connection:
   ```
   python manage.py check --database=default
   ```

## Create erabase_db Database (if it doesn't exist)

If the `erabase_db` database doesn't exist, create it:

1. Connect to PostgreSQL as admin:
   ```
   psql -U postgres -h localhost
   ```

2. Create the database:
   ```sql
   CREATE DATABASE erabase_db;
   CREATE SCHEMA IF NOT EXISTS public;
   \q
   ```

## Alternative: Continue with SQLite for now

Your current setup is working perfectly with SQLite. You can:
- Continue development with SQLite
- Switch to PostgreSQL/erabase_db later when you have the password
- All your machine maintenance data will work the same way 