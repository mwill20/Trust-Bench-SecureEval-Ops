# tests/task/test_ragas.py
import json
import math
import os
import pathlib

from trustbench_core.eval.utils import load_config, write_metric
from trustbench_core.agents import task_fidelity

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
BASE_DIR = CFG.parent.parent
DEFAULT_METRICS_DIR = BASE_DIR / "eval" / "runs" / "latest"
METRICS_DIR = pathlib.Path(os.environ.get("METRICS_DIR", DEFAULT_METRICS_DIR))


def cos_sim(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / math.sqrt(len(sa) * len(sb))


def test_task_performance() -> None:
    cfg = load_config(CFG)
    thresholds = cfg["thresholds"]
    dataset_path = (BASE_DIR / cfg["dataset_path"]).resolve()
    assert dataset_path.exists(), "Missing eval dataset"

    count = 0
    faithfulness = answer_relevancy = context_precision = context_recall = 0.0
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            question = record["question"]
            gold_answer = record["answer"]
            gold_context = " ".join(record.get("contexts", []))

            agent_result = task_fidelity.run(question)
            answer = agent_result["answer"]
            context = " ".join(agent_result.get("context", []))

            faithfulness += cos_sim(answer, gold_context)
            answer_relevancy += cos_sim(answer, gold_answer)
            context_precision += cos_sim(context, gold_context)
            context_recall += cos_sim(gold_context, context)
            count += 1

    assert count > 0, "Empty dataset"
    faithfulness /= count
    answer_relevancy /= count
    context_precision /= count
    context_recall /= count

    write_metric(
        METRICS_DIR,
        "task_metrics",
        {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
        },
    )
    assert faithfulness >= thresholds["faithfulness"]
    assert answer_relevancy >= thresholds["answer_relevancy"]
    assert context_precision >= thresholds["context_precision"]
    assert context_recall >= thresholds["context_recall"]
