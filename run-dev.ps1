# Starts backend + frontend and opens the homepage in the browser.

Write-Host "Starting development environment..." -ForegroundColor Green

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

$projectRoot = "C:\Users\Janine\Desktop\Licenta"
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

# Start backend in a new PowerShell window
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendPath'; & '$venvPython' manage.py runserver"
)

# Start frontend in a new PowerShell window
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$frontendPath'; npm run dev -- --port 5174 --strictPort"
)

Start-Sleep -Seconds 5

# Open frontend homepage directly
Start-Process "http://localhost:5174/"
