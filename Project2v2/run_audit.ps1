param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$RepoPath,
    
    [Parameter(Position=1)]
    [string]$OutputDir = "audit_output"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Trust Bench Multi-Agent Repository Auditor" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Note: Using system Python (virtual environment not required)

Write-Host "Analyzing repository: $RepoPath" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Green
Write-Host ""

# Run the multi-agent analysis
try {
    python main.py --repo $RepoPath --output $OutputDir
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "Analysis complete! Check the reports:" -ForegroundColor Green
    Write-Host "- JSON: $OutputDir\report.json" -ForegroundColor Yellow
    Write-Host "- Markdown: $OutputDir\report.md" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Green
    
    # Ask if user wants to view the report
    $view = Read-Host "Would you like to view the Markdown report now? (y/n)"
    if ($view -eq "y" -or $view -eq "Y") {
        Get-Content "$OutputDir\report.md" | Write-Host
    }
} catch {
    Write-Host "Error running analysis: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")