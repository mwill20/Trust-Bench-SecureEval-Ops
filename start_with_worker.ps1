#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start Trust Bench Studio with automatic job processing
.DESCRIPTION
    Starts both the backend API server and job processor worker in parallel
    so repository analyses complete automatically without manual intervention.
#>

param(
    [switch]$SkipInstall,
    [int]$Port = 8001,
    [string]$ServerHost = "127.0.0.1"
)

# Ensure we're in the right directory
Set-Location $PSScriptRoot

Write-Host "🚀 Starting Trust Bench Studio with Background Job Processing" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& .\\.venv\\Scripts\\Activate.ps1

# Set Python path
$env:PYTHONPATH = $PSScriptRoot

# Install dependencies if not skipped
if (-not $SkipInstall) {
    Write-Host "📋 Installing dependencies..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
}

# Function to cleanup processes on exit
function Cleanup {
    Write-Host "`n🛑 Shutting down services..." -ForegroundColor Yellow
    Get-Job | Stop-Job -Force
    Get-Job | Remove-Job -Force
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
        $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*job_processor*" 
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }
$null = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action { Cleanup; exit }

try {
    # Start backend server in background
    Write-Host "🔧 Starting backend API server on ${ServerHost}:${Port}..." -ForegroundColor Green
    $backendJob = Start-Job -ScriptBlock {
        param($ServerHost, $Port, $PythonPath)
        $env:PYTHONPATH = $PythonPath
        Set-Location $using:PSScriptRoot
        & .\\.venv\\Scripts\\Activate.ps1
        python -m uvicorn trust_bench_studio.api.server:app --host $ServerHost --port $Port --reload
    } -ArgumentList $ServerHost, $Port, $PSScriptRoot

    # Wait a moment for server to start
    Start-Sleep 3

    # Start job processor in background  
    Write-Host "⚙️  Starting background job processor..." -ForegroundColor Green
    $processorJob = Start-Job -ScriptBlock {
        param($PythonPath)
        $env:PYTHONPATH = $PythonPath
        Set-Location $using:PSScriptRoot
        & .\\.venv\\Scripts\\Activate.ps1
        python job_processor_demo.py
    } -ArgumentList $PSScriptRoot

    # Wait for both services to be ready
    Start-Sleep 2

    Write-Host "`n✅ Services started successfully!" -ForegroundColor Green
    Write-Host "🌐 Frontend: Open your browser and navigate to the UI" -ForegroundColor Cyan
    Write-Host "🔌 Backend API: http://${ServerHost}:${Port}" -ForegroundColor Cyan
    Write-Host "🤖 Job Processor: Running in background" -ForegroundColor Cyan
    Write-Host "`n📝 Repository analysis jobs will now complete automatically!" -ForegroundColor Yellow
    Write-Host "   - Submit a GitHub URL in the UI" -ForegroundColor Gray
    Write-Host "   - Jobs will be processed in the background" -ForegroundColor Gray
    Write-Host "   - Progress updates appear in real-time" -ForegroundColor Gray
    Write-Host "`n⏹️  Press Ctrl+C to stop all services" -ForegroundColor Red

    # Monitor both jobs and show their output
    while ($backendJob.State -eq "Running" -and $processorJob.State -eq "Running") {
        # Check for any job output
        $backendOutput = Receive-Job $backendJob -ErrorAction SilentlyContinue
        $processorOutput = Receive-Job $processorJob -ErrorAction SilentlyContinue
        
        if ($backendOutput) {
            Write-Host "[Backend] $backendOutput" -ForegroundColor Blue
        }
        if ($processorOutput) {
            Write-Host "[Processor] $processorOutput" -ForegroundColor Magenta
        }
        
        Start-Sleep 1
    }

} catch {
    Write-Host "❌ Error starting services: $_" -ForegroundColor Red
} finally {
    Cleanup
}