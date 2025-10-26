# Phase 3 Advanced Orchestration - Manual Testing Guide

## 🎯 Overview
Phase 3 introduces **Advanced Orchestration** with consensus building, conflict resolution, and iterative agent refinement. This guide walks you through testing these sophisticated multi-agent capabilities.

## 🚀 Getting Started

### Step 1: Start the Web Interface
```bash
cd "c:\Projects\Project 3\Trust-Bench-SecureEval-Ops\Project2v2"
python web_interface.py
```

**Expected Output:**
```
🎯 Starting Trust Bench Multi-Agent Auditor Web Interface...
🌐 Open your browser to: http://localhost:5000
🚀 Ready to analyze repositories!
```

### Step 2: Open Web Interface
1. Open your browser to: **http://localhost:5000**
2. You should see the Trust Bench Multi-Agent Auditor interface

### Step 3: Analyze a Repository
1. Click **"Analyze Repository"** button
2. Select **"test_repo"** from the dropdown
3. Wait for analysis to complete (you'll see progress indicators)

## 🧪 Phase 3 Testing Scenarios

### Scenario 1: Consensus Building Queries
Test queries that require agent consensus and negotiation:

**Test Query 1:**
```
What are the conflicting priorities between security and quality in this repository?
```

**Expected Phase 3 Indicators:**
- 🚀 **Orange banner:** "Phase 3 Advanced Orchestration - Consensus Building & Conflict Resolution"
- 🔄 **Orchestration Process:** Expandable section showing agent negotiations
- ✅ **Consensus Status:** "Consensus Achieved" or "Partial Consensus"
- 📊 **High Confidence:** 90%+ confidence scores
- 🎯 **Multiple Rounds:** Evidence of iterative agent refinement

**Test Query 2:**
```
Help me resolve the trade-offs between security hardening and code maintainability
```

**Test Query 3:**
```
What consensus can we reach on the most critical issues to address first?
```

### Scenario 2: Conflict Resolution Queries
Test the system's ability to detect and resolve agent disagreements:

**Test Query 4:**
```
Reconcile the different opinions between security and quality agents
```

**Test Query 5:**
```
Resolve any contradictions in the agent recommendations
```

### Scenario 3: Priority Negotiation
Test advanced orchestration for balancing competing priorities:

**Test Query 6:**
```
Which security issues should take priority over quality improvements?
```

**Test Query 7:**
```
How can we balance documentation needs with security and quality concerns?
```

## 🔍 What to Look For

### Phase 3 Visual Indicators
- **🚀 Phase 3 Banner:** Orange background with "Advanced Orchestration" text
- **🔄 Orchestration Process:** 
  - Click to expand and see agent negotiation logs
  - Multiple rounds of agent discussions
  - Conflict detection notes
  - Consensus building progress

### Phase 3 Response Quality
- **Higher Confidence Scores:** 90%+ (vs 70-80% for Phase 2)
- **Advanced Synthesis:** Unified recommendations that resolve conflicts
- **Priority Reconciliation:** Clear guidance on balancing competing concerns
- **Iterative Refinement:** Evidence agents refined their positions

### UI Behavior Verification
- **Consensus Status Updates:** Watch status change during processing
- **Process Logs:** Detailed orchestration steps visible when expanded
- **Agent Negotiations:** Multiple rounds of back-and-forth between agents

## ✅ Regression Testing

### Verify Phase 2 Still Works
Test these **Phase 2 queries** (should NOT trigger Phase 3):

```
Give me a comprehensive analysis of this repository
```

```
Provide complete security and quality assessment
```

**Expected:** Blue "Phase 2 Multi-Agent Consultation" banner

### Verify Phase 1 Still Works
Test these **single-agent queries** (should route to individual agents):

```
What security vulnerabilities exist?
```

```
How is the code quality?
```

**Expected:** Individual agent responses with persona indicators (🛡️, ⚡, 📚)

## 🎮 Interactive Testing Checklist

### Pre-Testing Setup
- [ ] Web server running at localhost:5000
- [ ] Repository analyzed (test_repo recommended)
- [ ] Browser ready for testing

### Phase 3 Core Features
- [ ] Consensus building queries trigger Phase 3 banner
- [ ] Orchestration process section appears and is expandable
- [ ] Consensus status updates during processing
- [ ] Higher confidence scores (90%+) displayed
- [ ] Advanced synthesis resolves apparent conflicts
- [ ] Multiple agent negotiation rounds visible in logs

### Phase 3 Advanced Features
- [ ] Conflict detection identifies disagreements
- [ ] Priority negotiation balances competing concerns
- [ ] Iterative refinement improves recommendations
- [ ] Final consensus represents unified agent position

### Regression Validation
- [ ] Phase 2 queries still trigger multi-agent consultation
- [ ] Single-agent queries still route correctly
- [ ] No UI errors or broken functionality
- [ ] All buttons and interactions working properly

## 🚨 Troubleshooting

### If Phase 3 Doesn't Trigger
1. **Check Query Wording:** Use keywords like "conflicting", "consensus", "resolve", "reconcile"
2. **Verify Repository Analysis:** Must analyze a repo first
3. **Check Console:** Look for JavaScript errors in browser dev tools

### If UI Elements Missing
1. **Refresh Page:** Clear browser cache if needed
2. **Check CSS:** Phase 3 styles should be loaded
3. **Verify Server Restart:** Web interface should auto-reload on changes

### If Responses Seem Wrong
1. **Check Agent Detection:** Should show multiple agents involved
2. **Verify Orchestration Level:** Should indicate "phase3" in response
3. **Review Process Logs:** Expand orchestration section for details

## 📊 Success Metrics

### Quality Indicators
- **Consensus Achievement:** Agents reach agreement on recommendations
- **Conflict Resolution:** Contradictions are identified and resolved
- **Priority Clarity:** Clear guidance on what to address first
- **Unified Voice:** Single coherent response despite multiple agents

### Technical Validation
- **Correct Routing:** Right queries trigger right orchestration levels
- **UI Consistency:** Visual indicators match orchestration complexity
- **Performance:** Responses complete in reasonable time
- **Stability:** No errors or crashes during testing

---

## 🎯 Quick Test Summary

**Fastest validation:** Use this single query to verify Phase 3:
```
What are the conflicting priorities between security and quality?
```

**Look for:** 🚀 Orange Phase 3 banner + 🔄 expandable orchestration process

**If working:** Phase 3 Advanced Orchestration is successfully implemented! 🎉