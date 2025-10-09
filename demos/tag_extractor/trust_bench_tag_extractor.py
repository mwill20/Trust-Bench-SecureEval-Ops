#!/usr/bin/env python3
"""
trust_bench_tag_extractor.py - Single-file Tag Extraction demo (deterministic fallback)
Run: python trust_bench_tag_extractor.py --demo
Options: --file <path> to analyze a text file
Outputs selected tags and writes a small report to /tmp/tag_report.md
This demo uses deterministic extractors and fallback selector/critic stubs.
"""

from __future__ import annotations
from typing import Set, List, Dict, Any, Optional
from pydantic import BaseModel
import argparse, re, json, textwrap, tempfile, time, os, sys, csv, pathlib

# ---------- State model ----------
class TagState(BaseModel):
    text: str
    k: int = 8
    gazetteer_hits: Set[str] = set()
    ner_hits: Set[str] = set()
    llm_hits: Set[str] = set()
    candidates: Set[str] = set()
    selected: List[str] = []
    critic_ok: bool = False
    retries: int = 0
    meta: Dict[str, Any] = {}

# ---------- Gazetteer extractor ----------
def gazetteer_extract(text: str, gaz_path: str) -> Set[str]:
    t = text.lower()
    hits = set()
    p = pathlib.Path(gaz_path)
    if not p.exists():
        return hits
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            term = row.get("term","").strip().lower()
            alias = row.get("alias","").strip().lower() if row.get("alias") else ""
            if not term:
                continue
            # word-boundary match for term or alias
            if re.search(rf"\\b{re.escape(term)}\\b", t):
                hits.add(normalize_tag(term))
            elif alias and re.search(rf"\\b{re.escape(alias)}\\b", t):
                hits.add(normalize_tag(term))
    return hits

# ---------- NER extractor (simple heuristic fallback) ----------
def ner_extract(text: str) -> Set[str]:
    # First try: extract common technical tokens and capitalized tech words
    tokens = set()
    # tech patterns: AWS, S3, Kubernetes, Docker, OAuth, REST, SQL, Redis, MongoDB
    tech_words = re.findall(r"\\b(?:[A-Z][a-z0-9\\-]+|AWS|S3|OAuth|Kubernetes|Docker|Redis|MongoDB)\\b", text)
    for t in tech_words:
        tokens.add(normalize_tag(t))
    # also extract dotted module/package names like aws.s3 or boto3
    pkg = re.findall(r"\\b[a-z0-9_\\.\\-]+\\.[a-z0-9_\\.\\-]+\\b", text.lower())
    for p in pkg:
        tokens.add(p.replace(".", "-"))
    return {t for t in tokens if len(t)>0}

# ---------- LLM extractor (stubbed: cheap heuristic) ----------
def llm_extract_stub(text: str, max_tags: int = 12) -> Set[str]:
    # Heuristic: take top nouns from first paragraph by frequency (simple splitting)
    first = text.strip().split("\\n\\n",1)[0]
    words = re.findall(r"\\b[a-zA-Z0-9\\-]{3,}\\b", first.lower())
    stop = {"the","and","for","with","that","this","from","using","using","project","model","dataset"}
    freq = {}
    for w in words:
        if w in stop: continue
        freq[w] = freq.get(w,0)+1
    # sort by frequency and pick distinct kebab-case tokens
    sorted_terms = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    picked = []
    for term,_ in sorted_terms:
        t = normalize_tag(term)
        if t not in picked:
            picked.append(t)
        if len(picked) >= max_tags:
            break
    return set(picked)

# ---------- Normalizer ----------
ALIASES = {
    "large-language-models":"llm",
    "large-language-model":"llm",
    "retrieval-augmented-generation":"rag",
    "retrieval-augmented-generator":"rag",
    "prompt-injection":"prompt-injection"
}
STOP = {"ai","ml","data","project","paper","model","models","dataset","datasets"}

def normalize_tag(t: str) -> str:
    t = t.strip().lower()
    t = re.sub(r"[^a-z0-9\\-\\s]","", t)
    t = re.sub(r"\\s+","-", t)
    t = ALIASES.get(t, t)
    if t in STOP: return ""
    return t

def normalize_union(*sets: Set[str]) -> Set[str]:
    out = set()
    for s in sets:
        for t in s or set():
            n = normalize_tag(t)
            if n: out.add(n)
    return out

# ---------- Selector (agentic logic stub + deterministic fallback) ----------
def selector_simple(candidates: Set[str], k: int, text: str) -> List[str]:
    # Score by presence count and token specificity (more hyphens/longer -> more specific)
    scores = {}
    low = text.lower()
    for c in candidates:
        if not c: continue
        freq = low.count(c.replace("-", " "))
        specificity = 1 + (len(c.split("-")) - 1) * 0.3
        scores[c] = freq * specificity + 0.001  # tiny floor
    sorted_c = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [t for t,_ in sorted_c][:k]

def selector_agent_stub(candidates:Set[str], k:int, text:str) -> List[str]:
    # This is where an LLM-selector would act. We'll use deterministic fallback.
    sel = selector_simple(candidates, k, text)
    return sel

# ---------- Critic (simple policy checks) ----------
def critic_check(tags: List[str], candidates:Set[str], text:str) -> Dict[str,Any]:
    # Rules: dedupe/aliases, ≤3 words per tag, at least one method/tool tag vs domain tag
    # For simplicity: method/tool tags often contain 'api', 'cli', 'sdk', 'oauth', 's3', 'sql', 'exec', 'shell'
    method_tokens = {"api","cli","sdk","oauth","s3","sql","exec","shell","curl","bash","power"} 
    domain_tokens = {"security","network","auth","storage","vision","nlp","bio"}
    # duplicates check (after normalizing already)
    if len(tags) != len(set(tags)):
        return {"ok": False, "fix": "duplicates present"}
    for t in tags:
        if len(t.split("-")) > 3:
            return {"ok": False, "fix": f"tag too long: {t}"}
    has_method = any(any(mt in t for mt in method_tokens) for t in tags)
    has_domain = any(any(dt in t for dt in domain_tokens) for t in tags)
    # consider anchored presence in text
    anchored = any(t in text.lower() for t in tags)
    if not anchored:
        return {"ok": False, "fix": "tags not grounded in text"}
    if not (has_method or has_domain):
        # not ideal, but allow and mark not-ok
        return {"ok": False, "fix": "need at least one method/tool or domain tag"}
    return {"ok": True}

# ---------- Runner / Orchestration (linear fallback) ----------
def run_tag_pipeline(text: str, k: int = 8, gaz_path: str = "data/gazetteer.csv", debug: bool=False) -> TagState:
    state = TagState(text=text, k=k)
    # extractors (parallel conceptually; we run sequentially)
    g_hits = gazetteer_extract(text, gaz_path)
    n_hits = ner_extract(text)
    l_hits = llm_extract_stub(text)
    state.gazetteer_hits = g_hits
    state.ner_hits = n_hits
    state.llm_hits = l_hits
    if debug:
        print("Gazetteer hits:", g_hits)
        print("NER hits:", n_hits)
        print("LLM hits:", l_hits)
    # normalize & union
    cand = normalize_union(g_hits, n_hits, l_hits)
    state.candidates = cand
    if debug:
        print("Normalized candidates:", cand)
    # selector (agent stub)
    sel = selector_agent_stub(cand, k, text)
    state.selected = sel
    # critic
    crit = critic_check(sel, cand, text)
    state.critic_ok = crit.get("ok", False)
    if not state.critic_ok:
        state.retries += 1
        # retry once with looser selection (include top raw candidates)
        if state.retries <= 2:
            # pick fallback: if nothing anchored, include top gazetteer or ner hits
            fallback_pool = list(cand)[: max(3, k)]
            sel = fallback_pool[:k]
            state.selected = sel
            crit = critic_check(sel, cand, text)
            state.critic_ok = crit.get("ok", False)
    # done
    state.meta = {"critic": crit, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return state

# ---------- Reporting ----------
def write_report(state: TagState, out_path: Optional[str]=None) -> str:
    if not out_path:
        out_path = os.path.join(tempfile.gettempdir(), "tag_report.md")
    lines = ["# Tag Extraction Report", ""]
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append("")
    lines.append("## Selected tags")
    for t in state.selected:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Candidates (sample)")
    cand_sample = list(state.candidates)[:50]
    if cand_sample:
        for t in cand_sample:
            lines.append(f"- {t}")
    lines.append("")
    lines.append("## Critic")
    lines.append(json.dumps(state.meta.get("critic", {})))
    open(out_path, "w", encoding="utf-8").write("\\n".join(lines))
    return out_path

# ---------- CLI ----------
def load_file_text(path: str) -> str:
    return open(path, "r", encoding="utf-8", errors="ignore").read()

def demo_texts_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")

def main():
    ap = argparse.ArgumentParser(description="trust_bench Tag Extraction Demo (single-file)")
    ap.add_argument("--file", help="Path to text file to analyze")
    ap.add_argument("--k", type=int, default=8, help="Number of tags to select")
    ap.add_argument("--demo", action="store_true", help="Run demo on built-in fixtures")
    ap.add_argument("--gazetteer", default=os.path.join(os.path.dirname(__file__), "data", "gazetteer.csv"), help="Gazetteer CSV path")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    if args.demo:
        fx = demo_texts_dir()
        # iterate sample fixtures
        for p in sorted(os.listdir(fx)):
            if not p.endswith(".txt"): continue
            path = os.path.join(fx, p)
            txt = load_file_text(path)
            print(f"--- Running demo on {p} ---")
            state = run_tag_pipeline(txt, k=args.k, gaz_path=args.gazetteer, debug=args.debug)
            out = write_report(state)
            print("Selected tags:", state.selected)
            print("Report:", out)
            print()
    else:
        if not args.file:
            print("Provide --file or --demo")
            return
        txt = load_file_text(args.file)
        state = run_tag_pipeline(txt, k=args.k, gaz_path=args.gazetteer, debug=args.debug)
        out = write_report(state)
        print("Selected tags:", state.selected)
        print("Report:", out)

if __name__ == '__main__':
    main()
