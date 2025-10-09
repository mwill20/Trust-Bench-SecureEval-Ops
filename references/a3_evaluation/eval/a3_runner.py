# eval/a3_runner.py
"""A3 Evaluation Runner (drop-in)
Reads a JSONL dataset of publications, computes per-row metrics:
  - title/tldr: simulated RAGAS metrics (semantic_similarity, faithfulness)
  - tags/references: jaccard overlap
  - coherence: simulated LLM-judge (0..1)
Produces CSV of scores and a markdown report with top failures.

Usage:
  python eval/a3_runner.py --dataset data/a3/sample.jsonl --out reports/a3_report.md --csv reports/a3_scores.csv --simulate
"""

import argparse, json, csv, pathlib, math
from collections import defaultdict

def norm(s: str) -> str:
    return " ".join(s.lower().split()) if isinstance(s, str) else ""

def jaccard(a, b):
    A = {norm(x) for x in (a or [])}
    B = {norm(x) for x in (b or [])}
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

def token_overlap(a, b):
    sa = set(norm(a).split())
    sb = set(norm(b).split())
    if not sa or not sb: return 0.0
    return len(sa & sb) / math.sqrt(len(sa) * len(sb))

def ragas_sim_metrics(candidate, reference, context):
    """Simulated RAGAS-style metrics:
       - semantic_similarity: token overlap proxy between candidate and reference
       - faithfulness: overlap between candidate and context
    """
    semsim = token_overlap(candidate, reference)
    faith = token_overlap(candidate, context)
    return {"semantic_similarity": semsim, "faithfulness": faith}

def coherence_simulator(publication_description, title_gen, tags_gen, tldr_gen):
    """Simulated LLM-judge coherence score (0..1) based on overlap across components and with context."""
    # score components: title vs desc, tldr vs desc, tag coverage
    s1 = token_overlap(title_gen, publication_description)
    s2 = token_overlap(tldr_gen, publication_description)
    # tags: fraction of tag tokens appearing in description
    tag_tokens = set(" ".join([norm(t) for t in tags_gen]).split())
    desc_tokens = set(norm(publication_description).split())
    tag_coverage = 0.0
    if tag_tokens:
        tag_coverage = len(tag_tokens & desc_tokens) / len(tag_tokens)
    # aggregate with weights
    score = 0.4 * s1 + 0.4 * s2 + 0.2 * tag_coverage
    # clamp
    return max(0.0, min(1.0, score))

def load_jsonl(path):
    p = pathlib.Path(path)
    assert p.exists(), f"Missing dataset: {path}"
    out = []
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out

def summarize_metrics(rows):
    agg = defaultdict(list)
    for r in rows:
        for k,v in r['metrics'].items():
            agg[k].append(v)
    summary = {}
    for k,v in agg.items():
        v_sorted = sorted(v)
        n = len(v_sorted)
        summary[k] = {
            'mean': sum(v_sorted)/n if n else 0.0,
            'p10': v_sorted[int(0.1*n)] if n else 0.0,
            'p50': v_sorted[int(0.5*n)] if n else 0.0,
            'p90': v_sorted[int(0.9*n)-1] if n else 0.0
        }
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--csv', required=True)
    ap.add_argument('--simulate', action='store_true', help='use simulated ragas/judge metrics')
    args = ap.parse_args()

    data = load_jsonl(args.dataset)
    results = []
    failures = []
    for rec in data:
        pub_id = rec.get('publication_id')
        desc = rec.get('publication_description','')
        title_truth = rec.get('title_truth','')
        tldr_truth = rec.get('tldr_truth','')
        title_gen = rec.get('title_generated','')
        tldr_gen = rec.get('tldr_generated','')
        tags_truth = rec.get('tags_truth',[])
        tags_gen = rec.get('tags_generated',[])
        refs_truth = rec.get('references_truth',[])
        refs_gen = rec.get('references_generated',[])

        title_metrics = ragas_sim_metrics(title_gen, title_truth, desc)
        tldr_metrics = ragas_sim_metrics(tldr_gen, tldr_truth, desc)
        tags_jac = jaccard(tags_truth, tags_gen)
        refs_jac = jaccard(refs_truth, refs_gen)
        coh = coherence_simulator(desc, title_gen, tags_gen, tldr_gen)

        metrics = {
            'title_semantic_similarity': title_metrics['semantic_similarity'],
            'title_faithfulness': title_metrics['faithfulness'],
            'tldr_semantic_similarity': tldr_metrics['semantic_similarity'],
            'tldr_faithfulness': tldr_metrics['faithfulness'],
            'tags_jaccard': tags_jac,
            'refs_jaccard': refs_jac,
            'coherence_score': coh
        }

        row = {'publication_id': pub_id, 'metrics': metrics, 'record': rec}
        results.append(row)

    # write CSV
    csv_path = pathlib.Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        header = ['publication_id'] + list(results[0]['metrics'].keys())
        writer.writerow(header)
        for r in results:
            writer.writerow([r['publication_id']] + [r['metrics'][k] for k in r['metrics']])

    # summary and failures (based on suggested thresholds)
    thresholds = {
        'title.semantic_similarity': 0.80,
        'title.faithfulness': 0.85,
        'tldr.semantic_similarity': 0.80,
        'tldr.faithfulness': 0.85,
        'tags.jaccard': 0.65,
        'references.jaccard': 0.60,
        'coherence.score': 0.80
    }

    # collect failures based on thresholds
    fail_list = []
    for r in results:
        m = r['metrics']
        reasons = []
        if m['title_semantic_similarity'] < thresholds['title.semantic_similarity']:
            reasons.append('title.semantic_similarity')
        if m['title_faithfulness'] < thresholds['title.faithfulness']:
            reasons.append('title.faithfulness')
        if m['tldr_semantic_similarity'] < thresholds['tldr.semantic_similarity']:
            reasons.append('tldr.semantic_similarity')
        if m['tldr_faithfulness'] < thresholds['tldr.faithfulness']:
            reasons.append('tldr.faithfulness')
        if m['tags_jaccard'] < thresholds['tags.jaccard']:
            reasons.append('tags.jaccard')
        if m['refs_jaccard'] < thresholds['references.jaccard']:
            reasons.append('refs.jaccard')
        if m['coherence_score'] < thresholds['coherence.score']:
            reasons.append('coherence.score')
        if reasons:
            fail_list.append({'publication_id': r['publication_id'], 'reasons': reasons, 'metrics': r['metrics']})

    summary = summarize_metrics(results)
    # write markdown report
    rpt = pathlib.Path(args.out)
    rpt.parent.mkdir(parents=True, exist_ok=True)
    md = []
    md.append('# A3 Eval Report\n')
    md.append('## Summary Metrics\n')
    for k,v in summary.items():
        md.append(f"- **{k}**: mean={v['mean']:.3f} p10={v['p10']:.3f} p50={v['p50']:.3f} p90={v['p90']:.3f}")
    md.append('\n## Failures\n')
    md.append(f"Total failures: {len(fail_list)}/{len(results)}\n")
    md.append('Top 5 failures:\n')
    for fitem in fail_list[:5]:
        md.append(f"- {fitem['publication_id']}: reasons={fitem['reasons']} metrics={fitem['metrics']}")
    rpt.write_text('\n'.join(md), encoding='utf-8')
    print('Wrote CSV ->', csv_path)
    print('Wrote report ->', rpt)

if __name__ == '__main__':
    main()
