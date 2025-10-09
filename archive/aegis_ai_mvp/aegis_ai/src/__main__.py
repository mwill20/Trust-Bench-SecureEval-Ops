\
import argparse, os, json
from .orchestrator import run_pipeline

def main():
    ap = argparse.ArgumentParser(prog="aegis_ai", description="Aegis.AI — Security Scanner MVP")
    ap.add_argument("--repo", required=True, help="GitHub URL or local path")
    ap.add_argument("--max-files", type=int, default=200, help="Max files to scan")
    ap.add_argument("--out", default="aegis_report.md", help="Report output path")
    args = ap.parse_args()

    state = {
        "repo": args.repo,
        "max_files": args.max_files,
        "out_path": args.out,
    }
    final = run_pipeline(state)
    print(json.dumps({
        "risk_report": final.get("report_path"),
        "findings": len(final.get("findings", [])),
    }, indent=2))

if __name__ == "__main__":
    main()
