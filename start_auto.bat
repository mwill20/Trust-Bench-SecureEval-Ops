@echo off
REM Trust Bench Studio - Automatic Startup with Background Job Processing
REM This script starts both the API server and job processor automatically

echo.
echo ================================================
echo  Trust Bench Studio - Full System Startup
echo ================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate Python environment
echo [1/3] Activating Python environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate Python environment
    echo Please ensure virtual environment exists: python -m venv .venv
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

REM Start both services
echo [2/3] Starting backend API server and job processor...
echo.
echo Starting services in background...

REM Use PowerShell to run the startup script
powershell -ExecutionPolicy Bypass -File "start_services.py"

echo.
echo [3/3] System ready!
echo.
echo ===============================================
echo  TRUST BENCH STUDIO IS NOW RUNNING
echo ===============================================
echo.
echo Services running:
echo   - Backend API Server (port 8001)
echo   - Job Processor Worker (background)
echo.
echo Repository analysis jobs will complete automatically!
echo.
echo Press Ctrl+C to stop all services
echo ===============================================

pause