Write-Host "Starting Machine Maintenance Logbook Servers..." -ForegroundColor Green
Write-Host ""

Write-Host "Starting Django Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd django_backend; python manage.py runserver 127.0.0.1:8000"

Write-Host "Waiting 3 seconds for Django to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "Starting React Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Django Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "React Frontend: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 