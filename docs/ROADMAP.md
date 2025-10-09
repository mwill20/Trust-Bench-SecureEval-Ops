# 🧭 TrustBench Development Roadmap & Rubric

This roadmap keeps the project aligned as it evolves from a working baseline into a full, deployable product.

---

## 🧩 PHASE 0 — Baseline Validation (✅ Completed)

**Goal:** Ensure core engine, reports, tests, and CI all function deterministically.

### Deliverables
- [x] Core agents wired and testable (`task_fidelity`, `security_eval`, `system_perf`, `ethics_refusal`)
- [x] Orchestrator produces metrics, gate.json, and report.html
- [x] CI workflows split: lint/tests + eval gate
- [x] Datasets, references, and examples consolidated with READMEs
- [x] Pytest passes locally and in CI

### Rubric Criteria
| Category | Metric | Threshold |
|-----------|---------|-----------|
| Test Coverage | ≥ 90% core files | ✅ |
| CI Stability | 100% runs succeed | ✅ |
| Documentation Clarity | Root + core README coherent, current | ✅ |
| Artifacts | report.html + metrics.json reproducible | ✅ |

---

## ⚙️ PHASE 1 — Real Agent Logic (In Progress)

**Goal:** Replace deterministic stubs with real model/tool integrations.

### Deliverables
- [ ] `task_fidelity` → RAGAS / retrieval accuracy check
- [ ] `security_eval` → PromptGuard, Semgrep, secrets scan (MCP-backed)
- [ ] `system_perf` → true latency tracking
- [ ] `ethics_refusal` → Groq LLM judge with refusal rubric
- [ ] Adjust thresholds to meaningful production levels
- [ ] Expand `profiles/highstakes.yaml` with realistic CI gate limits

### Rubric Criteria
| Category | Measure | Target |
|-----------|----------|--------|
| Integration Success | All agents execute without stubs | ✅ |
| Metric Validity | Scores vary realistically (non-static) | ✅ |
| Threshold Accuracy | <5% false failures over 10 runs | ✅ |
| Security Coverage | Injection-block, secrets-scan, refusal tests measurable | ✅ |

---

## 🧱 PHASE 2 — Studio App (TrustBench Studio)

**Goal:** Create a usable web interface for running and visualizing evaluations.

### Deliverables
- [ ] Streamlit app reads live reports (`trustbench_core/eval/runs/latest/`)
- [ ] User inputs repo URL or uploads dataset
- [ ] Scorecards with color-coded pillars
- [ ] Failure table with top artifacts and “Suggested Fix” hints
- [ ] Profile selector (default/highstakes/custom)
- [ ] Export: HTML/CSV/Markdown reports
- [ ] Optional: Login/session state for saved runs

### Rubric Criteria
| UX Category | Metric | Target |
|--------------|---------|--------|
| Usability | User runs eval in <60 sec from open | ✅ |
| Visibility | Metrics auto-refresh after run | ✅ |
| Clarity | Pass/fail visually distinct, labeled | ✅ |
| Reliability | No Streamlit crashes or subprocess errors | ✅ |

---

## 🧮 PHASE 3 — CI/CD + Gating Automation

**Goal:** Turn TrustBench into a CI-enforceable safety gate and analytics stream.

### Deliverables
- [ ] Enable `eval.yml` on default branch with required checks
- [ ] Auto-upload HTML/CSV artifacts for dashboards
- [ ] Slack or email notifications on CI failure
- [ ] Scheduled nightly “trust regression” runs
- [ ] Archive runs to `trustbench_core/eval/runs/history/`

### Rubric Criteria
| Area | Measure | Target |
|-------|----------|--------|
| Automation | CI auto-triggers eval on PR | ✅ |
| Artifact Retention | Reports for last 30 runs preserved | ✅ |
| Feedback Speed | <5 minutes to report completion | ✅ |
| Branch Protection | Gate enforced in GitHub settings | ✅ |

---

## 🔍 PHASE 4 — Evaluation Quality & Human Loop

**Goal:** Calibrate AI judgments with human feedback (HITL).

### Deliverables
- [ ] `hitl/labels.jsonl` with 30+ annotated examples
- [ ] `trustbench_core/eval/evaluate_agent.py` supports `--apply-hitl`
- [ ] `docs/playbooks/hitl.md` defines labeling rubric (faithfulness, refusal, safety)
- [ ] Comparison dashboard showing model vs. human agreement

### Rubric Criteria
| Aspect | Metric | Target |
|---------|---------|--------|
| Human Agreement | ≥ 85% alignment between judge & human | ✅ |
| Label Coverage | ≥ 30 samples per pillar | ✅ |
| Bias Check | <10% systematic deviation | ✅ |
| Documentation | HITL rubric published and versioned | ✅ |

---

## 📊 PHASE 5 — Trust Metrics Dashboard

**Goal:** Turn TrustBench data into a visual trend dashboard for long-term evaluation.

### Deliverables
- [ ] Aggregate metrics over time (faithfulness, refusal accuracy, latency)
- [ ] Trend chart (Streamlit or lightweight React)
- [ ] Comparative profiles (default vs highstakes vs experimental)
- [ ] Exportable CSV/JSON summaries for external dashboards

### Rubric Criteria
| Category | Measure | Target |
|-----------|----------|--------|
| Trend Accuracy | Data matches report.json history | ✅ |
| Visual Clarity | Charts update per new CI run | ✅ |
| Extensibility | New metric types pluggable without refactor | ✅ |

---

## 🏁 PHASE 6 — Publication-Ready Release

**Goal:** Deliver a stable, documented, demoable system.

### Deliverables
- [ ] Clean project tree with minimal redundancy
- [ ] Example notebook + video walkthrough
- [ ] LICENSE + CITATION.cff
- [ ] `CHANGELOG.md` for releases
- [ ] Deployed Studio app (Render, HuggingFace, or Streamlit Cloud)
- [ ] Final “TrustBench Overview” publication (markdown/pdf)

### Rubric Criteria
| Category | Measure | Target |
|-----------|----------|--------|
| Reproducibility | Full repo runs with one command | ✅ |
| Documentation | All READMEs current and linked | ✅ |
| Deployability | Streamlit app launches cleanly | ✅ |
| Presentation | Publication-quality artifact | ✅ |

---

## 📋 Rolling Checklist Summary

```
[✓] Baseline validation complete
[ ] Real agent logic integrated
[ ] Studio app live and interactive
[ ] CI gating enforced
[ ] HITL workflow active
[ ] Metrics dashboard implemented
[ ] Final release deployed
```

---

### Maintainer Notes
- Update this roadmap each milestone or release tag.
- Each phase completion should close with a CI-verified run + updated README badge.
- All future features should trace to one phase goal in this roadmap.
