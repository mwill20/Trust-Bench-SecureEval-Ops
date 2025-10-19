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
- Beautiful, modern web UI
- Real-time agent progress
- Color-coded results (excellent/good/fair/needs_attention)
- Interactive agent conversation logs
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

## 🎮 Fun Things to Try - See Collaboration in Action!

1. **Watch Collaboration Live:** Use the web interface to see agents communicate in real-time progress cards
2. **Compare Collaborative vs Individual Scores:** Notice how security findings reduce quality/documentation scores
3. **Test Cross-Agent Intelligence:** Create a file with fake credentials and watch how it impacts all three agents
4. **Study Conversation Logs:** Read detailed agent-to-agent messages in the final reports
5. **Analyze Documentation Gaps:** See how missing tests or security docs get caught through collaboration
6. **Custom Repository Analysis:** Point it at your own projects and discover collaborative insights
7. **Collaboration Metrics:** Check the final summary for collaboration statistics like "Agents collaborated on X cross-communications"

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