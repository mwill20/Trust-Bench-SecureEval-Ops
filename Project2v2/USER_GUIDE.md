# 🎯 User Guide: Trust Bench Multi-Agent Auditor

## 🚀 Ready to Use - Multiple Ways to Play!

Your multi-agent repository auditor is now set up and ready for exploration! Here are all the ways you can interact with it:

## 🌐 Option 1: Web Interface (Most User-Friendly)

**Status:** ✅ Running at http://localhost:5000

**How to use:**
1. The web interface is already running in your browser
2. Enter a repository path or choose from presets:
   - `.` = Current directory (Project2v2)
   - `..` = Parent directory (Trust_Bench_Clean) 
   - `test_repo` = Small test repository
3. Click "🔍 Analyze Repository"
4. Watch the agents work together in real-time!

**Features:**
- Beautiful, modern web UI with intelligent agent routing
- Real-time agent progress and specialized agent personas
- Color-coded results (excellent/good/fair/needs_attention)
- Interactive agent conversation logs
- **Phase 1: Smart Chat Interface**
  - 🛡️ Ask security questions → Routes to Security Agent
  - ⚡ Ask quality questions → Routes to Quality Agent  
  - 📚 Ask documentation questions → Routes to Documentation Agent
  - 🎯 General questions → Routes to Orchestrator Agent
- **Phase 2: Multi-Agent Consultation** 
  - 🔄 Comprehensive queries → Triggers multiple agents working together
  - 🎯 Multi-agent collaboration indicators show when specialists consult
  - 📋 Executive summaries synthesize input from all relevant agents
  - 🤝 Cross-domain analysis (e.g., "security and quality assessment")
- **Phase 3: Advanced Orchestration** ✨ NEW!
  - 🚀 Consensus building → Agents negotiate and reach unified decisions
  - ⚖️ Conflict resolution → Detects and resolves agent disagreements
  - 🔄 Iterative refinement → Multiple rounds of agent consultation
  - 🎯 Priority negotiation → Balances competing concerns (security vs quality)
  - 🤝 Advanced synthesis → Unified recommendations from complex negotiations
- Contextual responses with confidence scoring
- No command line needed!

## 🖥️ Option 2: Interactive Launcher

**Location:** `C:\Projects\Trust_Bench_Clean\Project2v2\launch.bat`

**How to use:**
1. Double-click `launch.bat` 
2. Choose from the menu:
   - CLI mode with examples
   - Web interface launcher
   - Quick analysis presets
   - Exit

## ⚡ Option 3: Quick Batch Scripts

**PowerShell (Recommended):**
```powershell
cd C:\Projects\Trust_Bench_Clean\Project2v2
.\run_audit.ps1 .                    # Analyze current directory
.\run_audit.ps1 ..                   # Analyze Trust_Bench_Clean
.\run_audit.ps1 test_repo             # Analyze test repository
```

**Windows Batch:**
```batch
cd C:\Projects\Trust_Bench_Clean\Project2v2
run_audit.bat .
run_audit.bat ..
run_audit.bat test_repo
```

## 🔧 Option 4: Direct Command Line

```powershell
cd C:\Projects\Trust_Bench_Clean\Project2v2
python main.py --repo . --output my_results
python main.py --repo .. --output parent_analysis
python main.py --repo test_repo --output test_results
```

## 📊 What You'll See - Enhanced Agent Collaboration

The agents will analyze any repository with **intelligent collaboration**:

### 🛡️ SecurityAgent (Proactive Communicator)
- Scans for AWS keys, GitHub tokens, private keys, etc.
- Rates security from 0-100 and shows exact file locations
- **NEW**: Immediately alerts other agents about security findings
- **Collaboration**: `"FYI: Found 5 security issues that may impact quality assessment"`

### 🔍 QualityAgent (Security-Aware Assessor)
- Analyzes code structure, languages, and test coverage  
- Rates overall code quality from 0-100
- **NEW**: Adjusts scores based on SecurityAgent findings (up to 25-point penalty)
- **Collaboration**: `"Adjusted quality score down by 25 points due to 5 security finding(s)"`

### 📝 DocumentationAgent (Context-Aware Reviewer)
- Reviews README files, counts sections, checks completeness
- **NEW**: Uses QualityAgent metrics (test coverage, file counts) in assessment
- **NEW**: Penalizes docs that don't address security or testing gaps  
- **Collaboration**: `"No tests found by QualityAgent - documentation lacks testing info"`

### 🤖 Manager (Collaboration Orchestrator)
- Coordinates all agents and tracks cross-communications
- Provides final composite score reflecting collaborative intelligence
- **NEW**: Reports collaboration metrics: `"Agents collaborated on 5 cross-communications"`
- Logs complete agent conversation showing decision-making process

## 🔄 Phase 2: Multi-Agent Consultation Features

**New in Phase 2:** The chat interface now supports advanced multi-agent consultation for comprehensive analysis.

### How Multi-Agent Consultation Works

**Single-Agent Queries** (route to one specialist):
- "Are there any security vulnerabilities?" → 🛡️ Security Agent only
- "How is the code quality?" → ⚡ Quality Agent only  
- "How good is the documentation?" → 📚 Documentation Agent only

**Multi-Agent Queries** (trigger collaborative analysis):
- "Give me a comprehensive analysis" → 🔄 All agents collaborate
- "What are the security and quality issues?" → 🛡️⚡ Security + Quality agents
- "Provide complete assessment of all aspects" → 🛡️⚡📚 Full team consultation

### Visual Indicators

When you ask multi-agent questions, you'll see:
- 🎯 **Collaboration indicator**: Shows which agents are consulting
- **Multiple agent avatars**: Visual representation of the team working together  
- **Executive summaries**: Synthesized responses combining all agent insights
- **Prioritized recommendations**: Actionable advice from collective analysis

### Example Multi-Agent Queries to Try

1. **Comprehensive Analysis**: "Give me a comprehensive analysis of this repository"
2. **Cross-Domain Assessment**: "What are the security and quality issues in this codebase?"  
3. **Full Evaluation**: "I need a thorough evaluation covering all aspects"
4. **Explicit Multi-Agent**: "Get input from security, quality, and documentation experts"

## 🚀 Phase 3: Advanced Orchestration Features

**New in Phase 3:** The most sophisticated multi-agent capabilities with consensus building, conflict resolution, and iterative refinement.

### How Advanced Orchestration Works

**Phase 3 Queries** trigger advanced consensus building when agents need to negotiate and resolve conflicts:

**Consensus Building Queries:**
- "What are the conflicting priorities between security and quality?" → 🚀 Advanced orchestration with negotiation
- "Help me resolve the trade-offs between security and quality" → 🔄 Iterative agent refinement
- "What consensus can we reach on the most critical issues?" → 🤝 Multi-round consensus building

**Conflict Resolution Queries:**
- "Reconcile the different opinions between security and quality agents" → ⚖️ Conflict detection and resolution
- "Resolve any contradictions in the agent recommendations" → 🎯 Priority negotiation

### Phase 3 Visual Indicators

When Phase 3 advanced orchestration activates, you'll see:
- 🚀 **Orange "Phase 3 Advanced Orchestration" banner** (vs blue Phase 2 banner)
- 🔄 **Orchestration Process section** (expandable) showing:
  - Multi-round agent negotiations
  - Conflict detection notes
  - Consensus building progress
  - Priority reconciliation steps
- ✅ **Consensus Status**: "Consensus Achieved", "Partial Consensus", or "In Progress"
- 📊 **Higher Confidence Scores**: 90%+ (vs 70-80% for Phase 2)
- 🎯 **Advanced Synthesis**: Unified recommendations that resolve apparent conflicts

### Example Phase 3 Queries to Try

1. **Priority Conflicts**: "What are the conflicting priorities between security and quality in this repository?"
2. **Trade-off Resolution**: "Help me resolve the trade-offs between security hardening and code maintainability"
3. **Consensus Building**: "What consensus can we reach on the most critical issues to address first?"
4. **Agent Reconciliation**: "Reconcile the different opinions between security and quality agents"
5. **Unified Strategy**: "Negotiate priorities and provide a unified action plan across all domains"

### Testing Phase 3 vs Phase 2

**Phase 2 Query** (multi-agent consultation):
```
"Give me a comprehensive analysis of this repository"
```
→ Triggers blue "Phase 2 Multi-Agent Consultation" banner

**Phase 3 Query** (advanced orchestration):  
```
"What are the conflicting priorities between security and quality?"
```
→ Triggers orange "Phase 3 Advanced Orchestration" banner with consensus building

## 🎮 Fun Things to Try - See All Phases in Action

1. **Watch Collaboration Live:** Use the web interface to see agents communicate in real-time progress cards
2. **Compare Single vs Multi-Agent:** Try "How is security?" vs "Give me comprehensive analysis"
3. **Test Cross-Agent Intelligence:** Create a file with fake credentials and watch how it impacts all three agents
4. **Study Conversation Logs:** Read detailed agent-to-agent messages in the final reports
5. **Analyze Documentation Gaps:** See how missing tests or security docs get caught through collaboration
6. **Custom Repository Analysis:** Point it at your own projects and discover collaborative insights
7. **Multi-Agent Synthesis:** Watch how comprehensive queries generate executive summaries
8. **Collaboration Metrics:** Check the final summary for collaboration statistics

## 📈 Expected Results

- **Project2v2:** ~61 points (fair) - good docs, no tests, clean security
- **Trust_Bench_Clean:** ~35 points (needs_attention) - many secrets, low test coverage
- **Test_repo:** ~52 points (fair) - clean but minimal
- **Your repositories:** Discover security issues and quality insights!

## 🔄 Currently Running

- ✅ Web Interface: http://localhost:5000 (active)
- ✅ All batch scripts ready to use
- ✅ Python environment configured
- ✅ All dependencies installed

**Go explore!** The system is completely functional and ready for hands-on experimentation. Try analyzing different repositories and see how the AI agents evaluate code security, quality, and documentation!

## Security Tips (Optional Hardening)

- Set the environment variable `ENABLE_SECURITY_FILTERS=true` (default) to enable stricter validation and sanitization for repository URLs and chat prompts.
- Disable the flag (`false`/`0`/`off`) temporarily if you need to compare behaviour or diagnose unexpected rejections.
- The new `security_utils.py` module houses the initial validators; extend it and add tests following the review → plan → build → test loop when you broaden coverage.
