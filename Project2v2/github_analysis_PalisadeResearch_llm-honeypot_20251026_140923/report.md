# Trust Bench Multi-Agent Evaluation Report
- Generated at: 2025-10-26T21:09:26.299442+00:00
- Repository: C:\Users\20mdw\AppData\Local\Temp\trustbench_PalisadeResearch_llm-honeypot__q_bwtwb

## Composite Summary
{
  "overall_score": 72.51,
  "grade": "good",
  "notes": "Weighted composite: Security(33%), Quality(33%), Docs(34%)",
  "calculation_method": "weighted",
  "individual_scores": {
    "security": 100.0,
    "quality": 28.0,
    "documentation": 89.02
  },
  "weights_used": {
    "security": 33,
    "quality": 33,
    "docs": 34
  }
}

## Evaluation Weight Configuration
**Scoring Method:** Custom Weighted Average

| Agent | Individual Score | Weight | Weighted Contribution |
| --- | --- | --- | --- |
| Security Agent | 100.0 | 33% | 33.0 |
| Quality Agent | 28.0 | 33% | 9.24 |
| Documentation Agent | 89.02 | 34% | 30.27 |

## Agent Findings
### SecurityAgent
- **Score:** 100.0
- **Confidence:** 🟡 MEDIUM - 76% (0.760)
- **Summary:** Scanned 67 files with no high-confidence secret matches.

### QualityAgent
- **Score:** 28.0
- **Confidence:** 🟡 MEDIUM - 70% (0.704)
- **Summary:** Indexed 69 files across 5 language group(s); 0 appear to be tests.

### DocumentationAgent
- **Score:** 89.02
- **Confidence:** 🟢 HIGH - 100% (1.000)
- **Summary:** Found 1 README file(s) with roughly 95 words and 3 section heading(s). (Adjusted based on quality metrics)


## Evaluation Metrics
| Metric | Value |
| --- | --- |
| System Latency (s) | 0.7884 |
| Faithfulness | 0.64 |
| Refusal Accuracy | 1.0 |
| SecurityAgent total (s) | 0.7827 |
| &nbsp;&nbsp;run_secret_scan (s) | 0.7826 |
| QualityAgent total (s) | 0.0031 |
| &nbsp;&nbsp;analyze_repository_structure (s) | 0.003 |
| DocumentationAgent total (s) | 0.0008 |
| &nbsp;&nbsp;evaluate_documentation (s) | 0.0007 |

## Conversation Log
- **Manager -> SecurityAgent:** Task assigned: Scan the repository for high-signal secrets or credentials.
- **Manager -> QualityAgent:** Task assigned: Summarize repository structure and gauge test coverage.
- **Manager -> DocumentationAgent:** Task assigned: Review README files and verify documentation depth.
- **SecurityAgent -> Manager:** Secret scan completed. Risk level: LOW (0 findings).
- **QualityAgent -> Manager:** Repository structure summarized. No security issues found - maintaining base quality score.
- **DocumentationAgent -> QualityAgent:** Used your metrics (files: 69, test ratio: 0.0%) to enhance documentation assessment.
- **DocumentationAgent -> Manager:** Documentation review finished. No tests found by QualityAgent - documentation lacks testing info - reduced score by 5
- **Manager -> All Agents:** Evaluation complete. Grade: GOOD (72.51 pts). Agents collaborated on 1 cross-communications. Collaborative adjustments: Documentation score adjusted based on quality metrics.