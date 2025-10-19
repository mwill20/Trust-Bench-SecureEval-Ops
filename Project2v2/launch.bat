@echo off
cd /d "C:\Projects\Trust_Bench_Clean\Project2v2"

REM Note: Using system Python (virtual environment not required)

:menu
cls
echo ============================================
echo    Trust Bench Multi-Agent Auditor
echo ============================================
echo.
echo Choose your interface:
echo.
echo 1. Command Line Interface (CLI)
echo 2. Web Interface (Browser)
echo 3. Quick Analysis of Trust_Bench_Clean
echo 4. Quick Analysis of Project2v2
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto cli
if "%choice%"=="2" goto web
if "%choice%"=="3" goto quick_parent
if "%choice%"=="4" goto quick_self
if "%choice%"=="5" goto exit
goto menu

:cli
echo.
echo ============================================
echo CLI Mode - Examples:
echo ============================================
echo.
echo To analyze current directory:
echo   python main.py --repo . --output results
echo.
echo To analyze parent directory:
echo   python main.py --repo .. --output results
echo.
echo To analyze specific path:
echo   python main.py --repo "C:\path\to\repo" --output results
echo.
echo Or use the convenient batch files:
echo   run_audit.bat .
echo   run_audit.bat ..
echo   run_audit.bat "C:\path\to\repo"
echo.
pause
goto menu

:web
echo.
echo Starting web interface...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python web_interface.py
pause
goto menu

:quick_parent
echo.
echo Analyzing Trust_Bench_Clean repository...
python main.py --repo .. --output quick_analysis_parent
echo.
echo Results saved to: quick_analysis_parent\
echo.
pause
goto menu

:quick_self
echo.
echo Analyzing Project2v2 repository...
python main.py --repo . --output quick_analysis_self
echo.
echo Results saved to: quick_analysis_self\
echo.
pause
goto menu

:exit
echo.
echo Goodbye!
exit