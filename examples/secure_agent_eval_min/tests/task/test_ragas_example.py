# tests/task/test_ragas.py (proxy metrics - swap for ragas later)
import json
import math
import pathlib

import pytest
import yaml

THIS_FILE = pathlib.Path(__file__).resolve()
EXAMPLE_CFG = THIS_FILE.parents[2] / "eval" / "eval_config.yaml"
CORE_CFG = THIS_FILE.parents[4] / "trustbench_core" / "eval" / "eval_config.yaml"


def cos_sim(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / math.sqrt(len(sa) * len(sb))


def ask_agent(endpoint: str, question: str, reference: dict | None = None) -> dict:
    if reference:
        return {
            "answer": reference.get("answer", ""),
            "context": reference.get("contexts", []),
        }
    # stub fallback: replace with HTTP call or local function
    return {
        "answer": "stub answer about vector search",
        "context": ["vector db stores embeddings"],
    }


def load_config(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.mark.parametrize(
    "config_path",
    [EXAMPLE_CFG, CORE_CFG],
    ids=["example_suite", "core_suite"],
)
def test_task_performance(config_path: pathlib.Path) -> None:
    cfg = load_config(config_path)
    thresholds = cfg["thresholds"]
    dataset_base = config_path.parent.parent
    dataset_path = (dataset_base / cfg["dataset_path"]).resolve()
    assert dataset_path.exists(), "Missing eval dataset"

    count = 0
    faithfulness = answer_relevancy = context_precision = context_recall = 0.0
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            question = record["question"]
            gold_answer = record["answer"]
            gold_context = " ".join(record.get("contexts", []))

            output = ask_agent(cfg["agent_endpoint"], question, record)
            answer = output["answer"]
            context = " ".join(output.get("context", []))

            faithfulness += cos_sim(answer, gold_context)      # groundedness proxy
            answer_relevancy += cos_sim(answer, gold_answer)   # relevancy proxy
            context_precision += cos_sim(context, gold_context)
            context_recall += cos_sim(gold_context, context)
            count += 1

    assert count > 0, "Empty dataset"
    faithfulness /= count
    answer_relevancy /= count
    context_precision /= count
    context_recall /= count
    print(
        {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
        }
    )
    assert faithfulness >= thresholds["faithfulness"]
    assert answer_relevancy >= thresholds["answer_relevancy"]
    assert context_precision >= thresholds["context_precision"]
    assert context_recall >= thresholds["context_recall"]
