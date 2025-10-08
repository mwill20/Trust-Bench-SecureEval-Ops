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
```bash
git clone https://github.com/mwill20/Trust_Bench.git
cd Trust_Bench
pip install -r requirements.txt
python -m trustbench_core.agents.task_fidelity
