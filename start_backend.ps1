# Start Trust Bench Studio Backend Server
# This script avoids PATH issues and starts the FastAPI backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Trust Bench Studio - Backend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please ensure .venv exists and is properly configured" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "OK - Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH to project root
Write-Host "[2/3] Setting PYTHONPATH..." -ForegroundColor Yellow
$env:PYTHONPATH = $ProjectRoot
Write-Host "PYTHONPATH=$env:PYTHONPATH" -ForegroundColor Gray
Write-Host ""

# Start uvicorn server
Write-Host "[3/3] Starting FastAPI backend server..." -ForegroundColor Yellow
Write-Host "Server will run on: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    uvicorn trust_bench_studio.api.server:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
