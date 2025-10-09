# SECURITY Notes (MVP)

This project is an educational MVP. It **does not** execute untrusted code. It scans text files for:
- Prompt‑injection indicators (role overrides, exfil requests, tool hijacks, obfuscation)
- Risky code patterns (curl|bash, eval/exec, weak crypto, unsafe deserialization)
- Dangerous command suggestions (rm -rf, chmod 777, etc.)

Hardening tips:
- Run in a sandboxed environment
- Keep the allowlist tight (extensions, max file sizes)
- Treat all outputs as triage, not final verdicts
