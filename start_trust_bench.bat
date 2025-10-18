@echo off
echo Starting Trust Bench System...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Execute the PowerShell script
powershell -ExecutionPolicy Bypass -File "start_simple.ps1" %*

REM Keep window open if there was an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)