@echo off
echo ============================================
echo    Trust Bench Multi-Agent Repository Auditor
echo ============================================
echo.

REM Note: Using system Python (virtual environment not required)

REM Check if repository path is provided
if "%1"=="" (
    echo Usage: run_audit.bat ^<repository_path^> [output_directory]
    echo.
    echo Examples:
    echo   run_audit.bat .                    ^(audit current directory^)
    echo   run_audit.bat ..                   ^(audit parent directory^)
    echo   run_audit.bat test_repo            ^(audit test_repo folder^)
    echo   run_audit.bat C:\path\to\repo      ^(audit specific path^)
    echo   run_audit.bat . my_output          ^(custom output directory^)
    echo.
    pause
    exit /b 1
)

REM Set default output directory if not provided
set OUTPUT_DIR=%2
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=audit_output

echo Analyzing repository: %1
echo Output directory: %OUTPUT_DIR%
echo.

REM Run the multi-agent analysis
python main.py --repo "%1" --output "%OUTPUT_DIR%"

echo.
echo ============================================
echo Analysis complete! Check the reports:
echo - JSON: %OUTPUT_DIR%\report.json
echo - Markdown: %OUTPUT_DIR%\report.md
echo ============================================
echo.
pause