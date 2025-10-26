# Phase 3 Manual Testing Walkthrough

## Step-by-Step Testing Instructions

### 🚀 Start the Server
1. Open PowerShell in the Project2v2 directory
2. Run: `python web_interface.py`
3. Wait for "Ready to analyze repositories!" message
4. Open http://localhost:5000 in your browser

### 🔍 Analyze a Repository
1. Click **"Analyze Repository"** button
2. Select **"test_repo"** from dropdown (recommended for testing)
3. Click **"Analyze"** 
4. Wait for analysis to complete (watch the progress indicators)

### 🧪 Test Phase 3 Advanced Orchestration

#### Test 1: Consensus Building Query
**Type this query:**
```
What are the conflicting priorities between security and quality in this repository?
```

**Look for these Phase 3 indicators:**
- 🚀 Orange banner: "Phase 3 Advanced Orchestration"
- 🔄 "Orchestration Process" section (click to expand)
- ✅ Consensus status indicator
- 📊 High confidence score (90%+)

#### Test 2: Conflict Resolution Query  
**Type this query:**
```
Help me resolve the trade-offs between security hardening and code maintainability
```

**Expected behavior:**
- Same orange Phase 3 banner
- Expanded orchestration logs showing agent negotiations
- Advanced synthesis resolving the trade-offs

#### Test 3: Priority Negotiation Query
**Type this query:**
```
Which security issues should take priority over quality improvements?
```

**Expected behavior:**
- Phase 3 orchestration with priority balancing
- Evidence of agents negotiating priorities
- Unified recommendations

### ✅ Verify Phase Separation

#### Test Phase 2 (should NOT trigger Phase 3)
**Type this query:**
```
Give me a comprehensive analysis of this repository
```

**Expected:** Blue "Phase 2 Multi-Agent Consultation" banner (NOT orange Phase 3)

#### Test Phase 1 (single agent)
**Type this query:**
```
What security vulnerabilities exist?
```

**Expected:** Single agent response with 🛡️ SecurityAgent persona

### 🎯 Success Criteria Checklist

- [ ] Phase 3 queries show orange "Advanced Orchestration" banner
- [ ] Orchestration Process section is expandable and shows agent negotiations
- [ ] Consensus status indicators appear and update
- [ ] Confidence scores are higher (90%+) for Phase 3
- [ ] Advanced synthesis resolves conflicts and balances priorities
- [ ] Phase 2 queries still work with blue banner (no regression)
- [ ] Single-agent queries still route correctly (no regression)
- [ ] No JavaScript errors in browser console
- [ ] All UI elements render correctly

### 🚨 If Something's Wrong

**Phase 3 not triggering?**
- Make sure you're using keywords like "conflicting", "consensus", "resolve", "reconcile"
- Check browser console for JavaScript errors
- Verify repository was analyzed first

**UI looks broken?**
- Refresh the page (Ctrl+F5)
- Check if web server restarted properly
- Look for error messages in PowerShell terminal

**Responses seem odd?**  
- Expand the "Orchestration Process" section to see what's happening
- Check if multiple agents are actually involved
- Verify the confidence scores and consensus status

---

## Quick Validation

**Fastest test:** Just ask:
```
What are the conflicting priorities between security and quality?
```

If you see the 🚀 orange "Phase 3 Advanced Orchestration" banner with an expandable 🔄 "Orchestration Process" section, Phase 3 is working! 🎉