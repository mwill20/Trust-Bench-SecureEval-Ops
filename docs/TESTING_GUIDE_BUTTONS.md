# Testing Guide: Trust Bench Studio Buttons

## Quick Start Testing

### 1. Prerequisites Check

```bash
# Ensure you're in the project root
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"

# Verify markdown2 is installed
python -c "import markdown2; print('✅ markdown2 installed')"

# Start backend server (Terminal 1)
python trust_bench_studio/api/server.py

# Start frontend dev server (Terminal 2)
cd trust_bench_studio/frontend
npm run dev
```

### 2. Test Report Generation

#### Command Line Test

```bash
# Generate a report directly
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
python scripts/generate_report.py
```

**Expected Output**:

```
📊 Generating TrustBench Evaluation Report...
✅ Report saved to: trustbench_core\eval\runs\latest\report.md
✅ HTML report saved to: trustbench_core\eval\runs\latest\report.html
✅ Report generation complete!
```

**Verification**:

- Check `trustbench_core/eval/runs/latest/report.html` exists
- Open in browser and verify formatting
- Check for all 4 pillar sections

#### UI Test

1. Open browser: `http://localhost:3000`
2. Hover over "Generate Report" button - tooltip should appear
3. Click "Generate Report"
4. Check logs panel for success message
5. Verify report created at `trustbench_core/eval/runs/latest/report.html`

### 3. Test Workspace Cleanup

#### Dry Run Test (Safe)

```bash
cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
python scripts/cleanup_workspace.py --dry-run
```

**Expected Output**:

```
🧹 Starting TrustBench Workspace Cleanup...
📂 Scanning evaluation runs (keeping 10 most recent)...
  ℹ️  No old runs found to archive
🗑️  Cleaning up temporary files...
  ✅ Cleaned: X.XX MB
============================================================
✅ Cleanup Complete!
📊 Summary:
  • Kept recent runs: N
  • Archived old runs: N
  • Total space freed: X.XX MB
============================================================
```

#### UI Test

1. Open browser: `http://localhost:3000`
2. Hover over "Cleanup Workspace" button - tooltip should appear
3. Click "Cleanup Workspace"
4. Confirmation dialog should appear
5. Click "OK" to proceed
6. Check logs panel for success message with disk space freed
7. Verify archives created in `trustbench_core/eval/runs/archive/`

### 4. Test Baseline Promotion

#### UI Test

1. Run a successful evaluation first:
   ```bash
   cd "c:\Users\20mdw\OneDrive\Desktop\SCHOOL\ReadyTensor.ai\Project 2"
   python run_eval_direct.py
   ```
2. Open browser: `http://localhost:3000`
3. Hover over "Promote to Baseline" button - tooltip should appear
4. Click "Promote to Baseline"
5. Confirmation dialog should appear
6. Click "OK" to proceed
7. Check logs panel for success message
8. Verify baseline created:
   ```bash
   dir trustbench_core\eval\runs\baseline
   ```
   Should show `metrics.json` and `metadata.json`

## Troubleshooting

### Issue: "markdown2 not found"

**Solution**:

```bash
pip install markdown2
```

### Issue: "Port already in use"

**Solution**:

```bash
# Find and kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Find and kill process on port 3000 (frontend)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### Issue: "No metrics found"

**Solution**: Run an evaluation first

```bash
python run_eval_direct.py
```

### Issue: Dev server compilation error

**Solution**: The duplicate declaration error should be fixed. If you see it:

1. Stop dev server (Ctrl+C)
2. Verify `App.tsx` has no duplicate handlers
3. Clear node_modules cache:
   ```bash
   cd trust_bench_studio/frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

### Issue: Backend API not responding

**Solution**:

1. Check backend is running: `http://127.0.0.1:8000/docs`
2. Check terminal for error messages
3. Restart backend server

### Issue: Report HTML looks unstyled

**Solution**: Check report.html contains embedded CSS in `<style>` tag

## Test Results Checklist

### ✅ Generate Report

- [ ] Command line script works
- [ ] Tooltip appears on hover
- [ ] Button click triggers API call
- [ ] Success message in logs
- [ ] report.html created
- [ ] HTML renders correctly in browser
- [ ] All 4 pillars shown
- [ ] CSS styling embedded
- [ ] Markdown formatting works

### ✅ Cleanup Workspace

- [ ] Dry run works without errors
- [ ] Tooltip appears on hover
- [ ] Confirmation dialog appears
- [ ] Cancel dialog works
- [ ] Button click triggers cleanup
- [ ] Success message with disk space
- [ ] Archives created in correct location
- [ ] Latest/baseline preserved
- [ ] Temp files cleaned

### ✅ Promote to Baseline

- [ ] Tooltip appears on hover
- [ ] Confirmation dialog appears
- [ ] Cancel dialog works
- [ ] Button click triggers promotion
- [ ] Success message in logs
- [ ] baseline/ directory created
- [ ] metrics.json copied
- [ ] metadata.json created
- [ ] Metadata contains timestamp and verdict

## Performance Benchmarks

### Report Generation

- **Expected Time**: 1-2 seconds
- **Output Size**: ~100-200 KB
- **Memory Usage**: <50 MB

### Workspace Cleanup

- **Expected Time**: 5-10 seconds (50 runs)
- **Space Freed**: 100-500 MB typically
- **Memory Usage**: <100 MB

### Baseline Promotion

- **Expected Time**: <1 second
- **Output Size**: ~50 KB
- **Memory Usage**: <10 MB

## Known Issues

### 1. Frontend Hot Reload

**Status**: Dev server may show stale errors after fixes
**Workaround**: Stop and restart dev server

### 2. Markdown Linting Warnings

**Status**: Cosmetic only (MD022/MD031/MD032)
**Impact**: None - does not affect functionality
**Action**: Can be ignored or fixed later

## Next Steps

After all tests pass:

1. Run full integration test with all buttons
2. Test error scenarios (network failures, disk full, etc.)
3. Test concurrent button clicks
4. Load test with multiple users
5. Document any edge cases found

## Test Environment

**Tested On**:

- OS: Windows
- Python: 3.13
- Node: Latest LTS
- Browser: Chrome/Edge
- Backend: FastAPI on port 8000
- Frontend: Vite/React on port 3000

---

**Last Updated**: 2025-01-28
**Version**: 1.0.0
**Status**: ✅ Core Tests Passing
