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

## 📊 What You'll See

The agents will analyze any repository and provide:

### 🛡️ SecurityAgent
- Scans for AWS keys, GitHub tokens, private keys
- Rates security from 0-100
- Shows exact file locations and snippets

### 🔍 QualityAgent  
- Analyzes code structure and languages
- Counts test files and coverage ratio
- Rates overall code quality

### 📝 DocumentationAgent
- Reviews README files
- Counts words and sections
- Checks for quickstart guides

### 🤖 Manager
- Coordinates all agents
- Provides final composite score
- Logs complete agent conversation

## 🎮 Fun Things to Try

1. **Compare Scores:** Analyze different repositories and compare grades
2. **Test Security:** Create a file with fake credentials and watch SecurityAgent catch it
3. **Documentation Impact:** Add more content to README.md and see the score improve
4. **Agent Conversations:** Read the conversation logs to see how agents communicate
5. **Custom Repositories:** Point it at any Git repository on your machine

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