Write-Host "Starting Machine Maintenance Logbook Servers..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Start Django Backend Server
Write-Host "Starting Django Backend on http://127.0.0.1:8000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd project\django_backend; python manage.py runserver 127.0.0.1:8000"

# Wait a moment for Django to start
Start-Sleep -Seconds 3

# Start React Frontend Server  
Write-Host "Starting React Frontend on http://127.0.0.1:5173" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd project; npm run dev"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Django Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "React Frontend: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
Read-Host 