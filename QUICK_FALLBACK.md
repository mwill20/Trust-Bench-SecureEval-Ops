# 🆘 QUICK FALLBACK REFERENCE

## 🛡️ **STABLE TAG: `v0.3.0-stable-auto-jobs`**

**If anything breaks, revert to this working state:**

```bash
# Quick revert method
git checkout v0.3.0-stable-auto-jobs

# Or create fallback branch
git checkout -b emergency-fallback v0.3.0-stable-auto-jobs
```

## ✅ **What Works:**
- ✅ Automatic repository analysis (10-15 seconds)
- ✅ Real-time UI progress updates  
- ✅ Background job processor
- ✅ End-to-end workflow: URL → Results

## 🚀 **Start Working System:**
```bash
# Option 1: Python service manager
python start_services.py

# Option 2: PowerShell 
.\start_with_worker.ps1

# Option 3: Batch file
start_auto.bat
```

## 🔍 **Quick Test:**
1. Start system (any method above)
2. Open UI in browser
3. Submit: `https://github.com/microsoft/vscode`  
4. Wait 10-15 seconds
5. See: Security Score, Code Quality, Issues Found

**📖 Full details:** See [FALLBACK_CONFIG.md](FALLBACK_CONFIG.md)