# Backend startup script for Django
# This script activates the virtual environment and runs the development server

Write-Host "Starting Django backend..." -ForegroundColor Green

# Set execution policy for this process
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Navigate to Downloads/S1DSA and activate the virtual environment there
$venvRoot = "C:\Users\Janine\Downloads\S1DSA"
cd $venvRoot
Write-Host "Changed to S1DSA: $venvRoot" -ForegroundColor Cyan

# Activate virtual environment from S1DSA
$venvActivate = Join-Path $venvRoot ".venv\Scripts\Activate.ps1"
Write-Host "Activating virtual environment from: $venvActivate" -ForegroundColor Cyan
& $venvActivate

# Navigate to the actual project backend (Desktop/Licenta/backend)
$projectRoot = "C:\Users\Janine\Desktop\Licenta"
$backendPath = Join-Path $projectRoot "backend"
cd $backendPath
Write-Host "Changed to backend: $backendPath" -ForegroundColor Cyan

# Run Django development server
Write-Host "Starting Django development server..." -ForegroundColor Green
python manage.py runserver
