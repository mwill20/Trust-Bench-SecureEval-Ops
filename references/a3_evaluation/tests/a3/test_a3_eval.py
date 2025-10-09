# tests/a3/test_a3_eval.py
import os, sys, subprocess, json, pathlib
from eval.utils import load_config

CFG = pathlib.Path(os.environ.get('EVAL_CFG','eval/eval_config.yaml'))

def test_a3_run():
    cfg = load_config(CFG)
    out_md = 'reports/a3_report.md'
    out_csv = 'reports/a3_scores.csv'
    cmd = [sys.executable, 'eval/a3_runner.py', '--dataset', 'data/a3/sample.jsonl', '--out', out_md, '--csv', out_csv, '--simulate']
    subprocess.check_call(cmd)
    assert pathlib.Path(out_md).exists(), 'report missing'
    assert pathlib.Path(out_csv).exists(), 'csv missing'
    # quick sanity check on csv content
    txt = pathlib.Path(out_csv).read_text(encoding='utf-8')
    assert 'publication_id' in txt
