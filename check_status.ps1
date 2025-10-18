# Trust Bench - System Status Checker
# Quickly check if all services are running

Write-Host ""
Write-Host "Trust Bench System Status Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$Services = @{
    "Backend API" = "http://localhost:8001/api/health"
    "Agent System" = "http://localhost:8001/api/agents" 
    "Frontend (3000)" = "http://localhost:3000"
    "Frontend (3001)" = "http://localhost:3001"
}

foreach ($service in $Services.GetEnumerator()) {
    $name = $service.Key
    $url = $service.Value
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] $name" -ForegroundColor Green -NoNewline
            Write-Host " - ONLINE" -ForegroundColor Gray
        } else {
            Write-Host "[ERROR] $name" -ForegroundColor Red -NoNewline  
            Write-Host " - HTTP $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "[OFFLINE] $name" -ForegroundColor Red -NoNewline
        Write-Host " - NOT RESPONDING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "If services are offline, run: .\start_simple.ps1" -ForegroundColor Yellow