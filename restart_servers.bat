@echo off
echo Restarting Machine Maintenance Logbook Servers...
echo.

echo Killing any existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo Waiting for processes to close...
timeout /t 3 /nobreak >nul

echo.
echo Starting Django Backend Server...
cd /d "%~dp0project\django_backend"
start "Django Backend" cmd /k "python manage.py runserver 127.0.0.1:8000"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting React Frontend Server...
cd /d "%~dp0project"
start "React Frontend" cmd /k "npm run dev"

echo.
echo ================================================
echo Servers are starting up...
echo Django Backend: http://127.0.0.1:8000
echo React Frontend: http://127.0.0.1:5173
echo ================================================
echo.
echo Both server windows should now be open.
echo Wait a few seconds for both servers to fully start,
echo then test your authentication in the browser.
echo.
pause 