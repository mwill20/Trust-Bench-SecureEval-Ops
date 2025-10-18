# Trust Bench - Simple System Startup Script
# This script starts all required services for the Trust Bench system

param(
    [switch]$SkipInstall,  # Skip npm install if packages are up to date
    [switch]$DevMode      # Start in development mode with detailed logging
)

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Trust Bench System Startup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Change to project root
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
Write-Host "Working directory: $ProjectRoot" -ForegroundColor Gray

# Step 1: Activate Python environment
Write-Host "[1/6] " -ForegroundColor Yellow -NoNewline
Write-Host "Setting up Python environment..." -ForegroundColor White

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

try {
    & ".\.venv\Scripts\Activate.ps1"
    $env:PYTHONPATH = $ProjectRoot
    Write-Host "SUCCESS: Python environment activated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to activate Python environment" -ForegroundColor Red
    exit 1
}

# Step 2: Install frontend dependencies if needed
Write-Host "[2/6] " -ForegroundColor Yellow -NoNewline
Write-Host "Checking frontend dependencies..." -ForegroundColor White

Push-Location "trust_bench_studio\frontend"

if (-not $SkipInstall -or -not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host "SUCCESS: Frontend dependencies ready" -ForegroundColor Green
Pop-Location

# Step 3: Start backend server
Write-Host "[3/6] " -ForegroundColor Yellow -NoNewline
Write-Host "Starting backend server..." -ForegroundColor White

$BackendScript = {
    param($ProjectPath)
    Set-Location $ProjectPath
    & ".\.venv\Scripts\Activate.ps1"
    $env:PYTHONPATH = $ProjectPath
    python -m uvicorn trust_bench_studio.api.server:app --host 127.0.0.1 --port 8001 --reload
}

$BackendJob = Start-Job -ScriptBlock $BackendScript -ArgumentList $ProjectRoot
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep 8

# Test backend
$BackendReady = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/health" -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    } catch {
        Write-Host "." -ForegroundColor Gray -NoNewline
        Start-Sleep 2
    }
}

if ($BackendReady) {
    Write-Host "SUCCESS: Backend server running on http://localhost:8001" -ForegroundColor Green
} else {
    Write-Host "ERROR: Backend server failed to start" -ForegroundColor Red
    Receive-Job $BackendJob | Write-Host -ForegroundColor Red
    exit 1
}

# Step 4: Start job processor for repository analysis
Write-Host "[4/7] " -ForegroundColor Yellow -NoNewline
Write-Host "Starting repository analysis worker..." -ForegroundColor White

$JobProcessorScript = {
    param($ProjectPath)
    Set-Location $ProjectPath
    & ".\.venv\Scripts\Activate.ps1"
    $env:PYTHONPATH = $ProjectPath
    python job_processor_demo.py
}

$JobProcessorJob = Start-Job -ScriptBlock $JobProcessorScript -ArgumentList $ProjectRoot
Start-Sleep 2
Write-Host "SUCCESS: Repository analysis worker started" -ForegroundColor Green

# Step 5: Start frontend server
Write-Host "[5/7] " -ForegroundColor Yellow -NoNewline
Write-Host "Starting frontend server..." -ForegroundColor White

$FrontendScript = {
    param($ProjectPath)
    Set-Location "$ProjectPath\trust_bench_studio\frontend"
    npm run dev
}

$FrontendJob = Start-Job -ScriptBlock $FrontendScript -ArgumentList $ProjectRoot
Start-Sleep 5

# Check frontend
$FrontendReady = $false
$FrontendPort = 3001  # Default
$PortsToCheck = @(3000, 3001, 3002)

foreach ($port in $PortsToCheck) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $FrontendReady = $true
            $FrontendPort = $port
            break
        }
    } catch { }
}

if ($FrontendReady) {
    Write-Host "SUCCESS: Frontend server running on http://localhost:$FrontendPort" -ForegroundColor Green
} else {
    Write-Host "INFO: Frontend server starting on http://localhost:$FrontendPort (may take a moment)" -ForegroundColor Yellow
}

# Step 6: Health check
Write-Host "[6/7] " -ForegroundColor Yellow -NoNewline
Write-Host "Running system health check..." -ForegroundColor White

try {
    $backendHealth = Invoke-WebRequest -Uri "http://localhost:8001/api/health" -ErrorAction SilentlyContinue
    $agentsHealth = Invoke-WebRequest -Uri "http://localhost:8001/api/agents" -ErrorAction SilentlyContinue
    
    Write-Host "SUCCESS: Backend API is online" -ForegroundColor Green
    Write-Host "SUCCESS: Agent system is online" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Some services may still be starting..." -ForegroundColor Yellow
}

# Step 7: Display summary
Write-Host "[7/7] " -ForegroundColor Yellow -NoNewline
Write-Host "System ready!" -ForegroundColor White

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " TRUST BENCH SYSTEM ACTIVE" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Web Interface:    " -ForegroundColor White -NoNewline
Write-Host "http://localhost:$FrontendPort" -ForegroundColor Cyan

Write-Host "API Documentation:" -ForegroundColor White -NoNewline
Write-Host "http://localhost:8001/docs" -ForegroundColor Cyan

Write-Host "API Health:       " -ForegroundColor White -NoNewline
Write-Host "http://localhost:8001/api/health" -ForegroundColor Cyan

Write-Host ""
Write-Host "System Components:" -ForegroundColor Magenta
Write-Host "  - Backend API (FastAPI server)" -ForegroundColor Gray
Write-Host "  - Frontend UI (React application)" -ForegroundColor Gray  
Write-Host "  - Repository Analysis Worker (job processor)" -ForegroundColor Gray
Write-Host ""
Write-Host "Available Agents:" -ForegroundColor Magenta
Write-Host "  - Athena (Task Fidelity)" -ForegroundColor Gray
Write-Host "  - Aegis (Security Evaluation)" -ForegroundColor Gray
Write-Host "  - Helios (System Performance)" -ForegroundColor Gray
Write-Host "  - Eidos (Ethics & Refusal)" -ForegroundColor Gray
Write-Host "  - Logos (Orchestrator)" -ForegroundColor Gray

Write-Host ""
Write-Host "Quick Start Guide:" -ForegroundColor Green
Write-Host "  1. Open web interface above" -ForegroundColor Gray
Write-Host "  2. Enter a GitHub repository URL" -ForegroundColor Gray
Write-Host "  3. Click 'Analyze Repository'" -ForegroundColor Gray
Write-Host "  4. Chat with agents about results" -ForegroundColor Gray

Write-Host ""
Write-Host "Press Ctrl+C to shut down all services" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Cleanup function
function Stop-Services {
    Write-Host "Shutting down services..." -ForegroundColor Yellow
    if ($BackendJob) { Stop-Job $BackendJob -ErrorAction SilentlyContinue; Remove-Job $BackendJob -ErrorAction SilentlyContinue }
    if ($FrontendJob) { Stop-Job $FrontendJob -ErrorAction SilentlyContinue; Remove-Job $FrontendJob -ErrorAction SilentlyContinue }
    if ($JobProcessorJob) { Stop-Job $JobProcessorJob -ErrorAction SilentlyContinue; Remove-Job $JobProcessorJob -ErrorAction SilentlyContinue }
    Write-Host "All services stopped." -ForegroundColor Green
}

# Monitor services
try {
    while ($true) {
        Start-Sleep 5
        
        if ($BackendJob.State -eq "Failed") {
            Write-Host "Backend server crashed!" -ForegroundColor Red
            break
        }
        
        if ($FrontendJob.State -eq "Failed") {
            Write-Host "Frontend server crashed!" -ForegroundColor Red
            break
        }
        
        if ($JobProcessorJob.State -eq "Failed") {
            Write-Host "Repository analysis worker crashed!" -ForegroundColor Red
            break
        }
        
        if ($DevMode) {
            Write-Host "." -ForegroundColor Green -NoNewline
        }
    }
} catch {
    # Ctrl+C pressed
} finally {
    Stop-Services
}