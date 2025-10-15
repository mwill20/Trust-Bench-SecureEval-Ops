# 🚀 Quick Fix for "Failed to Fetch" Error

## The Problem

The backend server keeps shutting down due to terminal interactions, causing the frontend to show "Failed to fetch" errors.

## ✅ Solution: Use the Startup Scripts

### Option 1: Using Batch Files (Recommended)

**Open TWO separate Command Prompt or PowerShell windows:**

#### Window 1: Backend

```cmd
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
start_backend.bat
```

Wait until you see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Window 2: Frontend

```cmd
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
start_frontend.bat
```

Wait until you see:

```
➜  Local:   http://localhost:3000/
```

### Option 2: Using PowerShell

#### Window 1: Backend

```powershell
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
.\start_backend.ps1
```

#### Window 2: Frontend

```powershell
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2\trust_bench_studio\frontend"
npm run dev
```

---

## Testing the Servers

### 1. Check Backend is Running

Open a NEW PowerShell window and run:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"
```

Should return:

```
status
------
ok
```

### 2. Check Frontend is Running

Open browser: http://localhost:3000

You should see the Trust Bench UI.

### 3. Test Reports API

In PowerShell:

```powershell
(Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reports/list").reports
```

Should show list of reports with verdicts and pillar scores.

---

## 🧪 Testing Milestone 1.2 (HTML Report Viewer)

Once both servers are running:

1. **Open browser**: http://localhost:3000

2. **Click "Reports"** in the left sidebar

3. **Verify Report List**:

   - ✅ See "latest" report
   - ✅ See verdict badge (PASS/FAIL/PARTIAL)
   - ✅ See color-coded pillar scores
   - ✅ See "View Report →" button

4. **Click "View Report →"**:

   - ✅ Report viewer loads
   - ✅ See header with metadata (ID, Repository, Verdict)
   - ✅ See report content formatted properly
   - ✅ See "← Back to List" button
   - ✅ See "📥 Download HTML" button

5. **Test Navigation**:

   - ✅ Click "← Back to List" → returns to report list
   - ✅ Click "View Report →" again → works

6. **Test Download**:
   - ✅ Click "📥 Download HTML"
   - ✅ File downloads as `report_latest.html`
   - ✅ Open downloaded file → matches displayed report

---

## ⚠️ Important Notes

### Keep Terminal Windows Open

- **DO NOT** run other commands in the terminal windows running the servers
- **DO NOT** close the terminal windows while using the app
- Use NEW terminal windows for testing commands

### If Backend Stops

1. Go back to the backend terminal window
2. Press Ctrl+C to fully stop it
3. Run `start_backend.bat` again

### If Frontend Stops

1. Go back to the frontend terminal window
2. Press Ctrl+C to fully stop it
3. Run `start_frontend.bat` again (or `npm run dev`)

---

## 🐛 Troubleshooting

### "Failed to fetch" Error

**Cause**: Backend not running or wrong port

**Fix**:

```powershell
# Check if backend is running
netstat -ano | findstr ":8000"

# If nothing appears, backend is not running
# Restart it with start_backend.bat
```

### "Cannot connect to localhost:3000"

**Cause**: Frontend not running

**Fix**:

```powershell
# Check if frontend is running
netstat -ano | findstr ":3000"

# If nothing appears, frontend is not running
# Restart it with start_frontend.bat or npm run dev
```

### Port Already in Use

**Backend (port 8000)**:

```powershell
# Find process using port 8000
netstat -ano | findstr ":8000"

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Then restart with start_backend.bat
```

**Frontend (port 3000)**:

```powershell
# Find process using port 3000
netstat -ano | findstr ":3000"

# Kill the process
taskkill /PID <PID> /F

# Then restart with start_frontend.bat
```

---

## ✅ Success Checklist

Before testing Milestone 1.2:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000 in browser
- [ ] Reports tab shows report list
- [ ] "View Report" button is clickable

---

**Last Updated**: October 14, 2025
**Status**: Both servers must be running in separate terminal windows
