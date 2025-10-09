# eval/methods/llm_judge.py
def llm_judge(reference:str, candidate:str, criteria:str="faithfulness"):
    ref = set(reference.lower().split())
    cand = set(candidate.lower().split())
    if not ref or not cand: return 1, "Empty text."
    overlap = len(ref & cand) / max(1,len(ref))
    score = 1 + int(overlap*4)
    return score, f"Proxy score for {criteria}: overlap={overlap:.2f}"
