# Trust Bench - Complete System Startup Script
# This script starts all required services for the Trust Bench system

param(
    [switch]$SkipInstall,  # Skip npm install if packages are up to date
    [switch]$DevMode      # Start in development mode with detailed logging
)

# Color functions for better output
function Write-Header($text) { 
    Write-Host "`n=============================================" -ForegroundColor Cyan
    Write-Host " $text" -ForegroundColor Cyan -NoNewline
    Write-Host "`n=============================================" -ForegroundColor Cyan
}

function Write-Step($step, $text) { 
    Write-Host "[$step] " -ForegroundColor Yellow -NoNewline
    Write-Host $text -ForegroundColor White
}

function Write-Success($text) { 
    Write-Host "✓ " -ForegroundColor Green -NoNewline
    Write-Host $text -ForegroundColor Green
}

function Write-Error($text) { 
    Write-Host "✗ " -ForegroundColor Red -NoNewline
    Write-Host $text -ForegroundColor Red
}

function Write-Info($text) { 
    Write-Host "ℹ " -ForegroundColor Blue -NoNewline
    Write-Host $text -ForegroundColor Gray
}

# Cleanup function for graceful shutdown
function Cleanup {
    Write-Header "Shutting Down Trust Bench System"
    
    if ($BackendJob) {
        Write-Step "1/3" "Stopping backend server..."
        Stop-Job $BackendJob -ErrorAction SilentlyContinue
        Remove-Job $BackendJob -ErrorAction SilentlyContinue
        Write-Success "Backend server stopped"
    }
    
    if ($FrontendJob) {
        Write-Step "2/3" "Stopping frontend server..."
        Stop-Job $FrontendJob -ErrorAction SilentlyContinue
        Remove-Job $FrontendJob -ErrorAction SilentlyContinue
        Write-Success "Frontend server stopped"
    }
    
    if ($MCPJob) {
        Write-Step "3/3" "Stopping MCP server..."
        Stop-Job $MCPJob -ErrorAction SilentlyContinue
        Remove-Job $MCPJob -ErrorAction SilentlyContinue
        Write-Success "MCP server stopped"
    }
    
    Write-Host "`nTrust Bench system has been shut down cleanly." -ForegroundColor Green
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Set up cleanup on Ctrl+C
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }
$null = Register-ObjectEvent -InputObject ([System.Console]) -EventName CancelKeyPress -Action { Cleanup; [System.Environment]::Exit(0) }

Write-Header "Trust Bench System Startup"
Write-Info "Starting complete Trust Bench evaluation platform..."

# Change to project root
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
Write-Info "Working directory: $ProjectRoot"

# Step 1: Verify and activate Python environment
Write-Step "1/8" "Setting up Python environment..."

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .venv"
    Write-Info "Please create a virtual environment first:"
    Write-Info "  python -m venv .venv"
    Write-Info "  .\.venv\Scripts\Activate.ps1"
    Write-Info "  pip install -r requirements.txt"
    exit 1
}

try {
    & ".\.venv\Scripts\Activate.ps1"
    $env:PYTHONPATH = $ProjectRoot
    Write-Success "Python environment activated"
} catch {
    Write-Error "Failed to activate Python environment: $($_.Exception.Message)"
    exit 1
}

# Step 2: Verify Python dependencies
Write-Step "2/8" "Checking Python dependencies..."
try {
    python -c "import uvicorn, fastapi, trust_bench_studio" 2>$null
    Write-Success "Python dependencies verified"
} catch {
    Write-Error "Missing Python dependencies. Installing..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install Python dependencies"
        exit 1
    }
    Write-Success "Python dependencies installed"
}

# Step 3: Check Node.js and frontend dependencies
Write-Step "3/8" "Setting up frontend environment..."

Push-Location "trust_bench_studio\frontend"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm not found. Please install Node.js"
    exit 1
}

if (-not (Test-Path "node_modules") -or -not $SkipInstall) {
    Write-Info "Installing frontend dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install frontend dependencies"
        exit 1
    }
}

Write-Success "Frontend environment ready"
Pop-Location

# Step 4: Start backend server
Write-Step "4/8" "Starting FastAPI backend server..."

$BackendScript = {
    param($ProjectPath)
    Set-Location $ProjectPath
    & ".\.venv\Scripts\Activate.ps1"
    $env:PYTHONPATH = $ProjectPath
    python -m uvicorn trust_bench_studio.api.server:app --host 127.0.0.1 --port 8001 --reload
}

$BackendJob = Start-Job -ScriptBlock $BackendScript -ArgumentList $ProjectRoot
Start-Sleep 3  # Give backend time to start

# Verify backend is running
$BackendReady = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    } catch {
        Start-Sleep 1
    }
}

if ($BackendReady) {
    Write-Success "Backend server running on http://localhost:8001"
} else {
    Write-Error "Backend server failed to start"
    Receive-Job $BackendJob | Write-Host
    exit 1
}

# Step 5: Start frontend server
Write-Step "5/8" "Starting React frontend server..."

$FrontendScript = {
    param($ProjectPath)
    Set-Location "$ProjectPath\trust_bench_studio\frontend"
    npm run dev
}

$FrontendJob = Start-Job -ScriptBlock $FrontendScript -ArgumentList $ProjectRoot
Start-Sleep 5  # Give frontend time to start

# Check if frontend is running
$FrontendReady = $false
$FrontendPort = $null
$PortsToCheck = @(3000, 3001, 3002)

foreach ($port in $PortsToCheck) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $FrontendReady = $true
            $FrontendPort = $port
            break
        }
    } catch {
        # Continue checking other ports
    }
}

if ($FrontendReady) {
    Write-Success "Frontend server running on http://localhost:$FrontendPort"
} else {
    Write-Info "Frontend server starting... (may take a moment)"
    $FrontendPort = 3001  # Default assumption
}

# Step 6: Start MCP server (if available)
Write-Step "6/8" "Starting MCP server..."

if (Test-Path "trust_bench_mcp\trust_bench_server.py") {
    $MCPScript = {
        param($ProjectPath)
        Set-Location $ProjectPath
        & ".\.venv\Scripts\Activate.ps1"
        $env:PYTHONPATH = $ProjectPath
        python trust_bench_mcp\trust_bench_server.py
    }
    
    $MCPJob = Start-Job -ScriptBlock $MCPScript -ArgumentList $ProjectRoot
    Start-Sleep 2
    Write-Success "MCP server started"
} else {
    Write-Info "MCP server not found (optional)"
}

# Step 7: System health check
Write-Step "7/8" "Running system health check..."

$HealthCheck = @{
    Backend = $false
    Frontend = $false
    Agents = $false
}

# Check backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/health" -ErrorAction SilentlyContinue
    $HealthCheck.Backend = ($response.StatusCode -eq 200)
} catch { }

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -ErrorAction SilentlyContinue
    $HealthCheck.Frontend = ($response.StatusCode -eq 200)
} catch { }

# Check agents endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/agents" -ErrorAction SilentlyContinue
    $HealthCheck.Agents = ($response.StatusCode -eq 200)
} catch { }

if ($HealthCheck.Backend) { Write-Success "Backend API: Online" } else { Write-Error "Backend API: Offline" }
if ($HealthCheck.Frontend) { Write-Success "Frontend UI: Online" } else { Write-Error "Frontend UI: Offline" }
if ($HealthCheck.Agents) { Write-Success "Agent System: Online" } else { Write-Error "Agent System: Offline" }

# Step 8: Display startup summary
Write-Step "8/8" "Trust Bench system ready!"

Write-Header "TRUST BENCH SYSTEM ACTIVE"

Write-Host ""
Write-Host "[WEB] " -ForegroundColor Blue -NoNewline
Write-Host "Web Interface: " -ForegroundColor White -NoNewline
Write-Host "http://localhost:$FrontendPort" -ForegroundColor Cyan

Write-Host "[API] " -ForegroundColor Blue -NoNewline  
Write-Host "API Documentation: " -ForegroundColor White -NoNewline
Write-Host "http://localhost:8001/docs" -ForegroundColor Cyan

Write-Host "[HEALTH] " -ForegroundColor Blue -NoNewline
Write-Host "API Health: " -ForegroundColor White -NoNewline
Write-Host "http://localhost:8001/api/health" -ForegroundColor Cyan

Write-Host ""
Write-Host "[AGENTS] " -ForegroundColor Magenta -NoNewline
Write-Host "Available Agents:" -ForegroundColor White
Write-Host "   - Athena (Task Fidelity)" -ForegroundColor Gray
Write-Host "   - Aegis (Security Evaluation)" -ForegroundColor Gray  
Write-Host "   - Helios (System Performance)" -ForegroundColor Gray
Write-Host "   - Eidos (Ethics & Refusal)" -ForegroundColor Gray
Write-Host "   - Logos (Orchestrator)" -ForegroundColor Gray

Write-Host ""
Write-Host "[GUIDE] " -ForegroundColor Green -NoNewline
Write-Host "Quick Start:" -ForegroundColor White
Write-Host "   1. Open web interface above" -ForegroundColor Gray
Write-Host "   2. Enter a GitHub repository URL" -ForegroundColor Gray
Write-Host "   3. Click 'Analyze Repository'" -ForegroundColor Gray
Write-Host "   4. Chat with agents about results" -ForegroundColor Gray

Write-Host ""
Write-Host "WARNING: " -ForegroundColor Yellow -NoNewline
Write-Host "Press " -ForegroundColor White -NoNewline
Write-Host "Ctrl+C" -ForegroundColor Red -NoNewline
Write-Host " to shut down all services" -ForegroundColor White

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan

# Keep the script running and monitor services
try {
    while ($true) {
        Start-Sleep 5
        
        # Check if any jobs failed
        if ($BackendJob.State -eq "Failed") {
            Write-Error "Backend server crashed!"
            Receive-Job $BackendJob | Write-Host -ForegroundColor Red
            break
        }
        
        if ($FrontendJob.State -eq "Failed") {
            Write-Error "Frontend server crashed!"
            Receive-Job $FrontendJob | Write-Host -ForegroundColor Red
            break
        }
        
        # Optional: Show status in development mode
        if ($DevMode) {
            Write-Host "." -ForegroundColor Green -NoNewline
        }
    }
} catch {
    # Ctrl+C or other interruption
} finally {
    Cleanup
}