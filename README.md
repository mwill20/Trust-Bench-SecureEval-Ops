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

### Option 1: Full System with Auto Job Processing ⭐ (Recommended)
**Repository analysis jobs complete automatically in the background!**

Simply double-click one of these files:
- **`start_auto.bat`** - Complete system with background job processor
- Or run: **`start_with_worker.ps1`** - PowerShell version with automatic processing
- Or run: **`start_services.py`** - Python-based service manager

```powershell
# Automatic job processing (recommended for normal use)
.\start_with_worker.ps1

# Or use the Python service manager
python start_services.py
```

### Option 2: Manual System Control
```powershell
# Full system startup (includes job processor)
.\start_simple.ps1

# Quick startup (skips dependency checks)  
.\start_simple.ps1 -SkipInstall
```

### Option 3: Development Setup
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
python job_processor_demo.py  # ⚡ Background worker for automatic job processing
npm run dev
