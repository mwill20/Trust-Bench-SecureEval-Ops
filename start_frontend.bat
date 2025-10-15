@echo off
REM Start Trust Bench Studio Frontend Development Server
REM This script handles PATH issues and starts the Vite dev server

cd /d "%~dp0trust_bench_studio\frontend"

echo ========================================
echo Trust Bench Studio - Frontend Startup
echo ========================================
echo.

echo Starting Vite development server...
echo Frontend will run on: http://localhost:3000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

npm run dev

echo.
echo Server stopped.
pause
