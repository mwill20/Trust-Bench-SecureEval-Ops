# 🧪 Trust_Bench

**Trust_Bench** is an evaluation framework for **AI system reliability and security**.  
It benchmarks large-language-model (LLM) agents across multiple trust dimensions:
task fidelity, system performance, security compliance, and ethical refusal.

---

## 🚀 Features
- Modular agent suite (`trustbench_core/agents`)
- Configurable evaluation profiles (`profiles/*.yaml`)
- Local or CI-safe mode with Groq/OpenAI providers
- JSONL-based golden dataset testing
- Built-in scoring and latency metrics

---

## 🧩 Quick Start

### Option 1: One-Click Startup (Recommended)
Simply double-click one of these files in Windows Explorer:

- **`start_trust_bench.bat`** - Complete system startup (first time)
- **`quick_start.bat`** - Fast startup for development (subsequent runs)

### Option 2: PowerShell Script
```powershell
# Full startup with dependency checks
.\start_trust_bench.ps1

# Quick startup (skips npm install)
.\start_trust_bench.ps1 -SkipInstall

# Development mode with detailed logging
.\start_trust_bench.ps1 -DevMode
```

### Option 3: Manual Setup
```bash
# Backend setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend setup
cd trust_bench_studio\frontend
npm install

# Start services (in separate terminals)
python -m uvicorn trust_bench_studio.api.server:app --host 127.0.0.1 --port 8001 --reload
npm run dev
