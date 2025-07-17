@echo off
echo Starting Machine Maintenance Logbook Servers...
echo ================================================

REM Start Django Backend Server
echo Starting Django Backend on http://127.0.0.1:8000
start "Django Backend" cmd /k "cd /d project\django_backend && python manage.py runserver 127.0.0.1:8000"

REM Wait a moment for Django to start
timeout /t 3 /nobreak

REM Start React Frontend Server
echo Starting React Frontend on http://127.0.0.1:5173
start "React Frontend" cmd /k "cd /d project && npm run dev"

echo.
echo Both servers are starting...
echo Django Backend: http://127.0.0.1:8000
echo React Frontend: http://127.0.0.1:5173
echo.
echo Press any key to exit...
pause 