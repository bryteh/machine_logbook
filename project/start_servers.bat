@echo off
echo Starting Machine Maintenance Logbook Servers...
echo.

echo Starting Django Backend Server...
start "Django Backend" cmd /k "cd django_backend && python manage.py runserver 127.0.0.1:8000"

echo Waiting 3 seconds for Django to start...
timeout /t 3 /nobreak >nul

echo Starting React Frontend Server...
start "React Frontend" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Django Backend: http://127.0.0.1:8000
echo React Frontend: http://127.0.0.1:5173
echo.
echo Press any key to exit...
pause >nul 