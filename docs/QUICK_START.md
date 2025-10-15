# Trust Bench Studio - Quick Start Guide

## Starting the Application

### Option 1: Using Batch Scripts (Recommended for Windows)

#### Start Backend Server

1. Double-click `start_backend.bat` in the project root
2. Server will start on http://127.0.0.1:8000
3. API docs available at http://127.0.0.1:8000/docs

#### Start Frontend Server

1. Double-click `start_frontend.bat` in the project root
2. Frontend will start on http://localhost:3000
3. Browser will automatically open

### Option 2: Using PowerShell Scripts

#### Start Backend Server

```powershell
.\start_backend.ps1
```

#### Start Frontend Server

```powershell
cd trust_bench_studio\frontend
npm run dev
```

### Option 3: Manual Start (if scripts don't work)

#### Backend Server

```powershell
# In project root
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
uvicorn trust_bench_studio.api.server:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Server

```powershell
# In project root
cd trust_bench_studio\frontend
npm run dev
```

## Testing the Report Viewer Feature

### Prerequisites

- Backend running on port 8000
- Frontend running on port 3000
- At least one evaluation report with HTML (we have `trustbench_core/eval/runs/latest/report.html`)

### Test Steps

1. **Open the Application**

   - Navigate to http://localhost:3000

2. **Go to Reports Tab**

   - Click "Reports" in the left sidebar
   - You should see a list of evaluation reports

3. **View a Report**

   - Click the "View Report →" button on the "latest" report
   - The HTML report should load in a formatted viewer

4. **Test Features**

   - ✅ Header shows: Report ID, Repository, Verdict
   - ✅ Report content displays with proper formatting
   - ✅ Report is scrollable
   - ✅ "Download HTML" button works
   - ✅ "← Back to List" button returns to report list

5. **Test Download**
   - Click "📥 Download HTML" button
   - File `report_latest.html` should download
   - Open downloaded file - should match displayed report

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'trust_bench_studio'`

**Solution**: Make sure PYTHONPATH is set:

```powershell
$env:PYTHONPATH = "C:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
```

**Error**: `No module named 'uvicorn'`

**Solution**: Install uvicorn in virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
pip install uvicorn
```

### Frontend won't start

**Error**: `Cannot find module 'vite'`

**Solution**: Install dependencies:

```powershell
cd trust_bench_studio\frontend
npm install
```

### Port already in use

**Error**: `Address already in use: 8000` or `EADDRINUSE: address already in use :::3000`

**Solution**: Kill existing processes:

```powershell
# Find and kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Find and kill process on port 3000 (frontend)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### PATH environment variable issues

**Error**: `The environment variable 'Path' seems to have some paths containing the '"' character`

**Solution**: Use the provided batch scripts (`start_backend.bat`, `start_frontend.bat`) which avoid PATH issues.

### Report viewer shows blank screen

**Possible causes**:

1. Backend not running - check http://127.0.0.1:8000/api/health
2. No HTML report exists - run an evaluation first
3. CORS issues - check browser console for errors

**Solution**: Ensure both servers are running and check browser console (F12) for error messages.

## API Endpoints (Backend)

Test these in your browser or with curl:

- Health Check: http://127.0.0.1:8000/api/health
- List Reports: http://127.0.0.1:8000/api/reports/list
- View Report: http://127.0.0.1:8000/api/reports/view/latest
- API Docs: http://127.0.0.1:8000/docs

## Current Implementation Status

✅ **Milestone 1.1**: Report History List - COMPLETE
✅ **Milestone 1.2**: HTML Report Viewer - COMPLETE (Testing in Progress)
⏳ **Milestone 1.3**: Baseline Comparison View - Next
⏳ **Milestone 1.4**: MCP Tool Activity Dashboard - Planned

## Need Help?

Check these files:

- `docs/MILESTONE_1_2_READY_FOR_TEST.md` - Detailed testing guide
- `docs/IMPLEMENTATION_PLAN.md` - Full roadmap
- `docs/USER_GUIDE_BUTTONS.md` - User documentation
- `docs/TESTING_GUIDE_BUTTONS.md` - Testing procedures

## Quick Commands Reference

```powershell
# Start backend (Option 1 - Batch)
start_backend.bat

# Start backend (Option 2 - PowerShell)
.\start_backend.ps1

# Start backend (Option 3 - Manual)
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
uvicorn trust_bench_studio.api.server:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
cd trust_bench_studio\frontend
npm run dev

# Test API
curl http://127.0.0.1:8000/api/reports/list

# Check server status
netstat -ano | findstr :8000  # Backend
netstat -ano | findstr :3000  # Frontend
```
