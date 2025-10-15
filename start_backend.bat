@echo off
REM Start Trust Bench Studio Backend Server
REM This script handles PATH issues and starts the FastAPI backend

cd /d "%~dp0"

echo ========================================
echo Trust Bench Studio - Backend Startup
echo ========================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Please ensure .venv exists and is properly configured
    pause
    exit /b 1
)
echo OK - Virtual environment activated
echo.

REM Set PYTHONPATH to project root
echo [2/3] Setting PYTHONPATH...
set PYTHONPATH=%CD%
echo PYTHONPATH=%PYTHONPATH%
echo.

REM Start uvicorn server
echo [3/3] Starting FastAPI backend server...
echo Server will run on: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

uvicorn trust_bench_studio.api.server:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Server stopped.
pause
